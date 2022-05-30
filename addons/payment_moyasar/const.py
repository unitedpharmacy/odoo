# Copyright 2022 Just Try.

PAYMENT_STATUS_MAPPING = {
    'pending': ('Pending',),
    'done': ('paid', 'succeeded'),
    'cancel': ('failed'),
}

API_KEY = 'sk_test_WjLCffmy5YzskVLRjUCHLc1qZ9w9ta9hSe9WXz3z'
PUBLISHABLE_API_KEY = 'pk_test_wVjjyzuBzLnvL8KVgpAvjLnA9uyi2Z55YnxGQkjP'
MOYASAR_PAGE_URL = 'http://alhassan.algorco.com:8071/moyasar/'
CALLBACK_URL = 'http://alhassan.algorco.com:8071/payment/moyasar/result'
AUTHORIZATION = "Basic c2tfdGVzdF9XakxDZmZteTVZenNrVkxSalVDSExjMXFaOXc5dGE5aFNlOVdYejN6Og=="