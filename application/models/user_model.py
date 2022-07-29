from application import app, DATABASE
from application.config.mysqlconnection import connectToMySQL
from application.models.player_model import Player
from flask_bcrypt import Bcrypt
import re
bcrypt = Bcrypt(app)

class User:
    
    TABLE_NAME = 'users'
    PLAYER_TABLE_NAME = Player.TABLE_NAME
    ATTR_TAGS = ['email','password']
    NAME_LENGTH = 3
    PASSWORD_LENGTH = 8
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    PASSWORD_REGEX = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])')
    
    def __init__(self, data) -> None:
        self.id = data['id']
        for tag in self.ATTR_TAGS:
            setattr(self, tag, data[tag])
        if 'player_id' in data:
            self.player_id = data['player_id']

    @classmethod
    def getAllUsers(cls):
        query = f'SELECT * FROM {cls.TABLE_NAME};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        user = [cls(user) for user in rslt]
        return user

    @classmethod
    def getUser(cls, user_data=None, id=False):
        query = f'SELECT * FROM {cls.TABLE_NAME} WHERE '
        query += 'email = %(email)s' if not id else f'id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query, user_data)
        return cls(rslt[0]) if rslt else False

    @classmethod
    def validateLogin(cls, creds):
        user_data = {
            'logged_user' : False,
        }
        cred_dict = {
            'email' : ('Please provide your email.', 'error_login_email'),
            'password' : ('Please enter your password.', 'error_login_pw')
            }
        fcheck = cls.flashCheck(creds, cred_dict)
        if fcheck:
            user_data['flash_msgs'] = fcheck
            return user_data
        current_user = cls.getUser(creds)
        if not current_user or not bcrypt.check_password_hash(current_user.password, creds['password']):
            user_data['flash_msgs'] = [{'error_login_creds':'Invalid credentials'}]
            return user_data
        current_player = Player.getPlayer(current_user.id)
        user_data['logged_user'] = {
            'id' : current_user.id,
            'email' : current_user.email,
            **current_player
            }
        return user_data

    @classmethod
    def validateRegist(cls, regist_info):
        regist_info_dict = {
            'name' : 
                (f'Your username must be at least {cls.NAME_LENGTH} characters long.', 
                 'error_reg_name',
                 len(regist_info['name']) >= cls.NAME_LENGTH),
            'email' : 
                ('Please provide a valid email.', 
                 'error_reg_email',
                 cls.EMAIL_REGEX.match(regist_info['email']) != None),
            'password' : 
                (f'Your password must include: at least {cls.PASSWORD_LENGTH} characters, an upper case letter, a lower case letter, a number, and a special character.', 
                 'error_reg_pw',
                 len(regist_info['password']) >= cls.PASSWORD_LENGTH,
                 cls.PASSWORD_REGEX.match(regist_info['password']) != None),
            'confirm_pw' : 
                ('Passwords must match.', 
                 'error_reg_conf_pw',
                 regist_info['password'] == regist_info['confirm_pw'])
        }
        return cls.flashCheck(regist_info, regist_info_dict)

    @classmethod
    def registerNewUser(cls, regist_info):
        user_data = {
            'logged_user' : False
        }
        reg_check = cls.validateRegist( regist_info )
        if reg_check:
            user_data['flash_msgs'] = reg_check
            return user_data
        query = f'SELECT * FROM {cls.TABLE_NAME} '
        query += 'WHERE email = %(email)s;'
        rslt = connectToMySQL(DATABASE).query_db(query, regist_info)
        if rslt:
            user_data['flash_msgs'] = [{
                'error_reg_email' : 'An account with this email has already been registered. Please try another.'
            }]
            return user_data
        new_user = cls.createNewUser(regist_info)
        current_player = Player.getPlayer(new_user.id)
        user_data['logged_user'] = {
            'id' : new_user.id,
            'email' : new_user.email,
            **current_player
            }
        return user_data

    @classmethod
    def createNewUser(cls, user_info):
        user_data = {
            'email' : user_info['email'],
            'password': bcrypt.generate_password_hash(user_info['password'])
        }
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.ATTR_TAGS)} ) "
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'%({tag})s' )
        cols = ', '.join(cols)
        query += f'VALUES( {cols} );'
        user_info['id'] = connectToMySQL(DATABASE).query_db(query, user_data)
        new_player = Player.createPlayer(name=user_info['name'], user_id=user_info['id'])
        new_user = cls(user_info)
        return new_user
    
    @classmethod
    def editUser(cls, new_info, id):
        new_info_dict = {
            'first_name' : 
                (f'Your first name must be at least {cls.NAME_LENGTH} characters long.', 
                 'error_update_fn',
                 len(new_info['first_name']) >= cls.NAME_LENGTH),
            'last_name' : 
                (f'Your last name must be at least {cls.NAME_LENGTH} characters long.', 
                 'error_update_ln',
                 len(new_info['last_name']) >= cls.NAME_LENGTH),
            'email' : 
                ('Please provide a valid email.', 
                 'error_update_email',
                 cls.EMAIL_REGEX.match(new_info['email']) != None)
        }
        if not cls.flashCheck(new_info, new_info_dict):
            return False
        current_user = cls.getUser(id=id)
        if current_user and current_user.email != new_info['email']:
            query = f'SELECT * FROM {cls.TABLE_NAME} '
            query += 'WHERE email = %(email)s;'
            rslt = connectToMySQL(DATABASE).query_db(query, new_info)
            if rslt:
                x = ('An account with this email has already been registered. Please try another.',
                    'error_update_email')
                return False
        query = f'UPDATE {cls.TABLE_NAME} '
        cols = []
        for tag in new_info_dict.keys():
            cols.append( f'{tag} = %({tag})s' )
        cols = ', '.join(cols)
        query += f'SET {cols} '
        query += f'WHERE id = {id};'
        print(query)
        rslt = connectToMySQL(DATABASE).query_db(query, new_info)

    @classmethod
    def subscribeUser(cls, user_id, item_id):
        query = f"INSERT INTO {cls.MTM_TABLE_NAME} ( users_id, magazines_id )"
        query += f'VALUES ( {user_id}, {item_id} );'
        rslt = connectToMySQL(DATABASE).query_db(query)
        return rslt

    @staticmethod
    def flashCheck(data, data_dict):
        invalidity = []
        for (k, v) in data_dict.items():
            if not data[k] or data[k] == '|':
                invalidity.append({v[1] : 'This field is required.'})
            elif not all(v):
                invalidity.append({v[1] : v[0]})
        return invalidity