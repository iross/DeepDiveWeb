import pdb
class DatabaseRouter(object):
    """
    A router to control all database operations on models in
    """
    def db_for_read(self, model, **hints):
        if model._meta.db_table and model._meta.app_label == "deepdive":
            return model._meta.db_table
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.db_table:
            return model._meta.db_table
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        if model._meta.db_table:
            return True
        return False

    def allow_syncdb(self, db, model):
        if db == 'articles':
            return model._meta.app_label == 'deepdive'
        return False
