import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
# ------------------------------------- #
from capstone import app, db
from capstone.models import Actor, Movie


now = datetime.now()

ASSISTANT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZ0VFVfdVU4aXJtbkdyQ1ZYWnRwOCJ9.eyJpc3MiOiJodHRwczovL21ya3VyYmFub3YxNDQudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDYwMTE2NzdkZGY3YjVhMDA3MThkZWE0NyIsImF1ZCI6ImNhcHN0b25lX2lkIiwiaWF0IjoxNjExNzUzNTcwLCJleHAiOjE2MTE3NjA3NzAsImF6cCI6ImZQWWJEdmwzOHdIaUVueXlVeld6OXh6RExCRThYZXY0Iiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9ycyIsInJlYWQ6bW92aWVzIl19.wUPS387AdpIxCXtafbUVzP4quyAwuUgB8SzumjITTcIQc49di510-MfndBnDVk-ZX30GVoAGMk_FST9Z6iNQkKfAt6VpYxgKtqlCjIjhDTZgzItnY_v8emG-qq3waquNJ4UEZjNxoYd8zBvWU8uMExZFoQN1oif3K_ND5Ia775V9Slnn5LOBOnuAZ5_5O_jb_Rv_-3hCmIGzHo538TWtYB4YvN2y-XPxo2ghWRpVlVz_69WDwa7HYFxM-900GdeJztilFg8ynhOSEiF4cExmmqoGthVayhzsmU2q69AGAdHK1vF6jZPgjuT6F4wb_JpcQweXZBzrcdRDxSaMLdmZBg"
DIRECTOR_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZ0VFVfdVU4aXJtbkdyQ1ZYWnRwOCJ9.eyJpc3MiOiJodHRwczovL21ya3VyYmFub3YxNDQudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDYwMTE2OGFjNjhiZjE4MDA2OWVkNzI0ZiIsImF1ZCI6ImNhcHN0b25lX2lkIiwiaWF0IjoxNjExNzUzNjg5LCJleHAiOjE2MTE3NjA4ODksImF6cCI6ImZQWWJEdmwzOHdIaUVueXlVeld6OXh6RExCRThYZXY0Iiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJhZGQ6YWN0b3IiLCJkZWxldGU6YWN0b3IiLCJtb2RpZnk6YWN0b3IiLCJtb2RpZnk6bW92aWUiLCJyZWFkOmFjdG9ycyIsInJlYWQ6bW92aWVzIl19.UdvE1ggSdeeHypg_Ulq7VNRyo5Q7CD0rrwZ3QEh4iHmcurQPTVLLi9iycXOegTF-5lTd4E9KCbcNfQ1fnyg1Pw_2a83e7HSerfyY3c1UYXInFzDPrC5BqSi4T24ZLS06jKYkQbsbYo1L7pCtIskNtAOlAl6bEZYTfNTKHbnbZn4IUuaojp52fsZoKpCxeCGI4SSiyBSwT_DrnHW7n3fRHNa8mA1H5_g3zOvqDcCUt-RW7Ei2Bl0o0mNB_ezWSd5lXIQsxw2PMVLPVfiTH3Odmb-vFVtRik-9Q495Yopfc_EsefbW-w65ZtDuCCJL0rC5hUhUNZfsD_Rf4lYTwu3G6Q"
PRODUCER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZ0VFVfdVU4aXJtbkdyQ1ZYWnRwOCJ9.eyJpc3MiOiJodHRwczovL21ya3VyYmFub3YxNDQudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDYwMTE2OTA4ZGY3YjVhMDA3MThkZWE3NCIsImF1ZCI6ImNhcHN0b25lX2lkIiwiaWF0IjoxNjExNzUzNzk3LCJleHAiOjE2MTE3NjA5OTcsImF6cCI6ImZQWWJEdmwzOHdIaUVueXlVeld6OXh6RExCRThYZXY0Iiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJhZGQ6YWN0b3IiLCJhZGQ6bW92aWUiLCJkZWxldGU6YWN0b3IiLCJkZWxldGU6bW92aWUiLCJtb2RpZnk6YWN0b3IiLCJtb2RpZnk6bW92aWUiLCJyZWFkOmFjdG9ycyIsInJlYWQ6bW92aWVzIl19.l_iuCKZKI0fSxcCKQ1Y31ihvwDRjz-Xmv9ShoW6rT6sAX6LfRRHUC0XSJYPW_7Jo9C-k5h0JJCUYMwNw7bcpY1FRi_LxzssCpSIw1G2nJewkGhJr89UqCODb0avrN-MAAJqa96UHwYJqEpmMs92pDva7rpG9wRgMgxsmM98nPe6IuZw4WF45WpVa1YzaDqG1rqp6Vbi4AIp72OeIz1scW76CYwm2DcWA8mi0XF2xHQwdzoZ4YMhvsoSz9IA6qqg8plDyHRuox0VsBUIgo8JjVm66ZqLlS60LH59EdQ6n-ZxNETTvrkzD9aC5ti9Y0j7mvKpU0Y5C2uqTUdKvcnJ84g"

class CastingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client

    def tearDown(self):
        pass

    data_actor = {
        "name": "Ashton Kutcher", 
        "age": 42, 
        "gender": "Male"}

    data_movie = {
        "title": "Jobs", 
        "release_date": now}

    # POST /actors
    def test_add_actor(self):
        # Add new actors
        res = self.client()\
            .post("/actors", json=data_actor, headers=DIRECTOR_TOKEN)

        data = json.loads(res.data)
        Fout = open( "capstone/tests/test_add_actor.txt","w" ) 
        Fout.write(str(data))
        Fout.close()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])


    # POST /actors
    def test_add_actor_401(self):
        # Add new actor => without authorization header
        res = self.client()\
            .post("/actors", json=data_actor)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Authorization header is expected.")

    # POST /actors
    def test_add_actor_400(self):
        # add new actor => without ['name']
        this_actor = {"age": 45}
        res = self.client()\
            .post("/actors", json=this_actor, headers=DIRECTOR_TOKEN)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Please add 'name' in the json")

    # GET /actors
    def test_get_actors(self):
        # get actors at from page 1
        res = self.client().get("/actors", headers=ASSISTANT_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    # GET /actors
    def test_get_actors_404(self):
        # get actors from page 100
        res = self.client().get("/actors?page=100", headers=ASSISTANT_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "OOPS! No actors willing to work")

    # GET /actors
    def test_get_actors_401(self):
        # get actors => without authorization header
        res = self.client().get("/actors")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Authorization header is expected.")

    # PATCH /actors/id
    def test_modify_actors_400(self):
        # update actor => without json data
        res = self.client().patch("/actors/1", headers=PRODUCER_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "there is no json body")

    # PATCH /actors/id    
    def test_modify_actors_403(self):
        # update actor => by assistant header == without permissions
        this_actor = {"name": "Jason Staham"}
        res = self.client().patch("/actors/1", json=this_actor, headers=ASSISTANT_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Permission not found.")

    # DELETE /actors
    def test_delete_actor_404(self):
        # Delete actor => incorrect actor_id
        res = self.client().delete("/actors/10", headers=PRODUCER_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "No actor with this id")

    # DELETE /actors
    def test_delete_actor_401(self):
        # Delete actor => without headers
        res = self.client().delete("/actors/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Authorization header is expected.")

    # DELETE /actors
    def test_delete_actor(self):
        # Delete actor - testing for Success
        res = self.client().delete("/actors/1", headers=PRODUCER_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # Post /movies
    def test_add_movie_401(self):
        # Add new movie = > without authorization header
        res = self.client().post("/movies", json=data_movie)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Authorization header is expected.")


    # GET /movies
    def test_get_movies(self):
        # Get movie data at page 1
        res = self.client().get("/movies?page=1", headers=ASSISTANT_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    # GET /movies
    def test_get_movies_404(self):
        # Get movie data at page 100
        res = self.client().get("/movies?page=100", headers=ASSISTANT_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "OOPS! No one is making movies")


    # PATCH /movies
    def test_modify_movies(self):
        # Update a movie => testing for success
        movie = {"title": "Forsaj 9"}
        res = self.client().patch(
            "/movies/1", json=movie, headers=PRODUCER_TOKEN
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["movie"], 1)

    def test_modify_movies_400(self):
        # Update a movie => not sending json
        res = self.client().patch("/movies/1", headers=PRODUCER_TOKEN)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "there is no json body")


if __name__ == "__main__":
    unittest.main()

