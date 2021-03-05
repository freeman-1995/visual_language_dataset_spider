import os

def launch_database_server():
    cwd = os.getcwd()
    print(cwd)

    # launch redis server
    os.system("redis-server {}".format(os.path.join(cwd, "database", "redis.conf")))

    # launch mongodb server
    os.system("mongod -f {}".format(os.path.join(cwd, "database", "mongodb.conf")))