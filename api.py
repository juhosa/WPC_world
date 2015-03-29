from flask import Flask, request
from flask.ext.restful import Api, abort, Resource, fields, marshal, reqparse
import psycopg2 as pg

app = Flask(__name__)
api = Api(app)

conn = pg.connect("dbname=wpc user=postgres")
cur = conn.cursor()

point_fields = {
    'lat': fields.Float,
    'lng': fields.Float,
    'nick': fields.String
}

class MapPoints(Resource):
    def get(self):
        sql = "SELECT lat,lng,nick FROM map_points"
        cur.execute(sql)
        ret = cur.fetchall()
        
        column_names = [desc[0] for desc in cur.description]    
            
        ret2 = []
        for i in ret:
            tmp = {}
            for j,e in enumerate(i):                
                tmp[column_names[j]] = e
            ret2.append(tmp)
        
        return {'map_points': [marshal(map_point, point_fields) for map_point in ret2]}, 200, {'Access-Control-Allow-Origin': '*'}
        
class MapPoint(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('lat', type=str, required=True)
        self.reqparse.add_argument('lng', type=str, required=True)
        self.reqparse.add_argument('nick', type=str, required=False)
        super(MapPoint, self).__init__()    
        
    def post(self):
        args = self.reqparse.parse_args()
        nick = args['nick']
        lat = args['lat']
        lng = args['lng']
        
        data = (lat, lng, nick)
        
        sql = "INSERT INTO map_points (lat, lng, nick) VALUES (%s, %s, %s)"
        
        cur.execute(sql, data)
        conn.commit()
        
        ret = {'lat': lat, 'lng': lng, 'nick': nick }
        
        return marshal(ret, point_fields), 201, {'Access-Control-Allow-Origin': '*'}
        
api.add_resource(MapPoint, '/mappoint/add')
api.add_resource(MapPoints, '/mappoints')

if __name__ == '__main__':
    app.run(debug=True)
