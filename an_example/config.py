import redis

Redis = redis.StrictRedis(host='localhost',port=6379,db=0)
pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=1)
pool_redis = redis.StrictRedis(connection_pool=pool)

