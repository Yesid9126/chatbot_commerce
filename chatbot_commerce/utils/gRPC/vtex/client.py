import grpc
try:
    from chatbot_commerce.utils.gRPC.vtex.products import products_pb2_grpc, products_pb2
except:
    from products import products_pb2_grpc, products_pb2

class VtexService:

    def __init__(self, store=None):
        self.store = store

    def all_products(self):
        with grpc.insecure_channel('localhost:60867') as channel:
            stub = products_pb2_grpc.ProductControllerStub(channel)
            response = stub.List(products_pb2.ProductListRequest())
            for product in response:
                print(product)
            return response

if __name__ == '__main__':
    a = VtexService()
    a.all_products()
else:
    print(__name__)
    print('Hola')