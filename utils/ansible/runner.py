from utils.redis_client import RedisOperator
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C
import sys
from .callback import ModelResultsCollector
from utils.redis_client import RedisOperator
from collections import namedtuple
from multiprocessing import current_process

r = RedisOperator('ansible_db')


class ANSRunner(object):
    def __init__(self, server_list):
        print("Init ANSRunner")
        current_process()._config = {'semprefix': '/mp'}
        self.loader = DataLoader()
        self.inventory = InventoryManager(loader=self.loader, sources=server_list)
        self.variable_manager = VariableManager(self.loader, self.inventory)
        self.passwords = {}
        self.callback = ModelResultsCollector()
        context.CLIARGS = ImmutableDict(connection='smart', forks=40, become=None, become_method=None, become_user=None,
                                        check=False, diff=False, verbosity=3)
        print("ANSRunner init complete")

    def run_model(self, host_list, module_name, module_args):
        print('Running ANSRunner')
        play_source = dict(
            name='Ansible Ad-hoc',
            hosts=host_list,
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name, args=module_args))]
        )
        play = Play().load(play_source, loader=self.loader, variable_manager=self.variable_manager)
        tqm = None
        print("Ready to play")
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback=self.callback
            )
            C.HOST_KEY_CHECKING = False
            tqm.run(play)
            print("Play ran")
        except Exception as err:
            r.set("exception", err)
        finally:
            if tqm is not None:
                print("Clean tqm")
                tqm.cleanup()
            if self.loader:
                print("Clean loader")
                self.loader.cleanup_all_tmp_files()
