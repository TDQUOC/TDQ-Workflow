import json
import pytest

def paths(a,b,p=""):
    if a==b: return []
    if isinstance(a,dict) and isinstance(b,dict):
        return [x for k in sorted(set(a)|set(b)) for x in paths(a.get(k),b.get(k),p+"/"+k)]
    return [p]

@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item,nextitem):
    runner=item.module.runner
    original=runner._finish_run
    original_fp=runner.tdq_test_receipt.build_fingerprint
    previous=[]
    def fingerprint(*args,**kwargs):
        value=original_fp(*args,**kwargs)
        if previous:
            print("TDQ_FINGERPRINT_DIFF "+json.dumps(paths(previous[-1],value)),flush=True)
        previous.append(value)
        return value
    def finish(result,before,after,*args):
        print("TDQ_FINAL_DIFF "+json.dumps(paths(before,after)),flush=True)
        return original(result,before,after,*args)
    runner._finish_run=finish
    runner.tdq_test_receipt.build_fingerprint=fingerprint
    try:
        result=yield
    finally:
        runner._finish_run=original
        runner.tdq_test_receipt.build_fingerprint=original_fp
    return result
