import unittest

# from app import db,User,Movie,app,forge,initdb
from watchlist import db,app
from watchlist.models import User,Movie
from watchlist.commands import forge,initdb

class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        self.all = db.create_all()
        user = User(name='test',username='test')
        user.set_password('1234')
        movie = Movie(title='movie title',year='1222')
        db.session.add_all({user,movie})
        db.session.commit()

        self.client = app.test_client()
        self.runner = app.test_cli_runner()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    def test_app_exist(self):
        self.assertIsNotNone(app)
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])
    def test_404_page(self):
        response = self.client.get('/nothing')  #请求路径,nothing没有写，所以是404
        data = response.get_data(as_text=True)
        self.assertIn('404 Page not found',data)
        self.assertIn('Go back', data)
        self.assertEqual(404,response.status_code)
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('test\'s Watchlist',data)
        self.assertIn('movie title',data)
        self.assertEqual(response.status_code,200)
    #辅助方法
    def login(self):
        self.client.post('/login',data=dict(
            username='test',password='1234'
        ),follow_redirects=True)
    def test_create_item(self):
        self.login()

        response = self.client.post('/', data=dict(
            title='New movie', year='1232'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('New movie',data)
        self.assertIn('Item created.', data)

        response = self.client.post('/', data=dict(
            title='New movie', year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

        response = self.client.post('/', data=dict(
            title='', year='1232'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)
    def test_update_item(self):
        self.login()

        response = self.client.post('/movie/edit/1',data=dict(
            title = 'New movie',year='1232'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('New movie', data)
        self.assertIn('1232', data)
        self.assertIn('Item update.',data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='New movie', year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item update.',data)
        self.assertIn('Invalid input.',data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='', year='1232'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item update.', data)
        self.assertIn('Invalid input.', data)
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted',data)
        self.assertNotIn('movie title',data)
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings',data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    def test_login(self):
        response = self.client.post('/login',data=dict(
            username = 'test',password = '1234'         #TODO
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login Success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        response = self.client.post('/login', data=dict(
            username='testuser', password='1111'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login Success.', data)
        self.assertIn('Invalid username or password.', data)

        response = self.client.post('/login', data=dict(
            username='wrong',
            password='1234'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login Success.', data)
        self.assertIn('Invalid username or password.', data)

        response = self.client.post('/login', data=dict(
            username='',
            password='1234'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login Success.', data)
        self.assertIn('Invalid input', data)

        response = self.client.post('/login', data=dict(
            username='testuser',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login Success.', data)
        self.assertIn('Invalid input', data)

    def test_logout(self):
        self.login()

        response = self.client.get('/logout',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Good Bye!',data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
    def test_settings(self):
        self.login()

        response = self.client.get('/settings',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings',data)
        self.assertIn('Your Name',data)

        response = self.client.post('/settings',data=dict(
            name='update_user'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings update',data)
        self.assertIn('update_user',data)

        response = self.client.post('/settings', data=dict(
            name=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings update', data)
        self.assertIn('Invalid input.', data)
    #测试虚拟数据
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done.',result.output)
        self.assertNotEqual(Movie.query.count(),0)
    def test_init_db_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database',result.output)
    #测试生成管理员账户
    def test_admin_create(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin','--username','Admin(BeYC)','--password','1234'])
        self.assertIn('Creating User',result.output)
        self.assertIn('Done.',result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username,'Admin(BeYC)')
        self.assertTrue(User.query.first().validate_password('1234'))
    #Testing updating Admin account
    def test_admin_update(self):
        result = self.runner.invoke(args=['admin','--username','Admin','--password','12345'])
        self.assertIn('Updating User.',result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'Admin')
        self.assertTrue(User.query.first().validate_password('12345'))


if __name__ == '__main__':
    unittest.main()