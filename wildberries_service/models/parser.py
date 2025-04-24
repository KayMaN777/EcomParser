
# Mock function to simulate data retrieval
def mock_data():
    return {
        "product_id": 123456789,
        "name": "Sample Product",
        "brand": "Sample Brand",
        "price": 1000,
        "discount_price": 800,
        "rating": 4.5,
        "reviews": 150,
    }

class WildberriesParser:
    def __init__(self):
        pass

    def search(self, text, num, order):
        data = [mock_data() for _ in range(num)]
        return {
            'filename': 'mock search',
            'data': data
        }

    def category(self, link, num, order):
        data = [mock_data() for _ in range(num)]
        return {
            'filename': 'mock category',
            'data': data
        }

    def seller(self, link, num, order):
        data = [mock_data() for _ in range(num)]
        return {
            'filename': 'mock seller',
            'data': data
        }
