#!/usr/bin/env python


from picas.actors import RunActor
from picas.clients import CouchDB


class ExampleActor(RunActor):
    def __init__(self, db, view, **viewargs):
        super(ExampleActor, self).__init__(db, view, **viewargs)

    def prepare_env(self, *kargs, **kvargs):
        pass

    def prepare_run(self, *kargs, **kvargs):
        pass

    def process_task(self, ref, token):
        # this is where all the work gets done. Start editing here.
        print(token)

    def cleanup_run(self, *kargs, **kvargs):
        pass

    def cleanup_env(self, *kargs, **kvargs):
        pass


def main():
    db = CouchDB(url="http://localhost:5984", db='test')
    actor = ExampleActor(db, 'todo')
    actor.run()


if __name__ == '__main__':
    main()
