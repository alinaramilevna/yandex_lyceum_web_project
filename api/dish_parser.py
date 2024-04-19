from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('weight', required=True)
parser.add_argument('description', required=True)
parser.add_argument('structure', required=True)
parser.add_argument('price', required=True, type=int)
parser.add_argument('type_id', required=True, type=int)
parser.add_argument('image_id', required=True, type=int)
