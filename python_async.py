import asyncio
import time

def menssage(delay):
    time.sleep(1)
    print(delay)
    return delay

loop = asyncio.new_event_loop()
async def hola(loop):
    start = time.time()
    asynciofunctions = [loop.run_in_executor(None, menssage, i) for i in list(range(100))[::-1]]
    result = [await asynciofunction for asynciofunction in asynciofunctions]
    asynciofunctions = [loop.run_in_executor(None, menssage, i) for i in list(range(50))[::-1]]
    result2 = [await asynciofunction for asynciofunction in asynciofunctions]
    print(time.time() - start)
    return result, result2

result = loop.run_until_complete(hola(loop=loop))
loop.close()
print('mi resultado',result)