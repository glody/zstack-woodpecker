'''

New Integration Test for expunging KVM VM and check capacity by QueryPrimaryStorage.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
import os

_config_ = {
        'timeout' : 200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
delete_policy = None

def test():
    global delete_policy
    delete_policy = test_lib.lib_set_delete_policy('vm', 'Delay')
    test_util.test_dsc('Test storage capacity when using expunge vm')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('No Enabled/Connected primary storage was found, skip test.' )
        return True

    ps = ps[0]

    avail_cap = ps.availableCapacity

    vm = test_stub.create_vm(vm_name = 'basic-test-vm')
    test_obj_dict.add_vm(vm)
    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)[0]
    avail_cap1 = ps.availableCapacity
    if avail_cap == avail_cap1:
        test_util.test_fail('PS capacity is same after create vm. Capacity before create vm: %s, after create vm: %s ' % (avail_cap, avail_cap1))
    time.sleep(1)
    vm.destroy()
    vm.expunge()
    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)[0]
    avail_cap2 = ps.availableCapacity
    if avail_cap != avail_cap2:
        test_util.test_fail('PS capacity is not same after create/expunge vm. Capacity before create vm: %s, after expunge vm: %s ' % (avail_cap, avail_cap2))
    test_lib.lib_set_delete_policy('vm', delete_policy)
    test_util.test_pass('Expunge VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_lib.lib_set_delete_policy('vm', delete_policy)
