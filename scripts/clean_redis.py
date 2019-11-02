from redis import Redis
import os

try:
  redis_conn = Redis(os.getenv("REDIS_HOSTNAME", default="localhost"), port=6379)
except:
  redis_conn = Redis(os.getenv("REDIS_HOSTNAME", default="redis"), port=6379)

def delete_keys():
    redis_conn.flushall()
    print("Deleted keys")
    return True

if __name__ == "__main__":
    delete_keys()