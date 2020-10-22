

class ACLrepo(object):
    
    def __init__(self,acl_store_dir):
        self.acl_store_dir = acl_store_dir
        
    def dumps(self, replace_path=None, force=False):
        raise NotImplementedError
    
    def loads(self,replace_path=None ):
        raise NotImplementedError
    
    def remove_sync(self, all_acl ):
        raise NotImplementedError
    
    