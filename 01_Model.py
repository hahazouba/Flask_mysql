# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class BookForm(FlaskForm):
    """自定义表单"""
    author = StringField(u'作者：', validators=[DataRequired()])
    book = StringField(u'书名：', validators=[DataRequired()])
    submit = SubmitField(u'添加')



app = Flask(__name__)

# 配置秘钥：csrf,flash_message,session
app.config['SECRET_KEY'] = 'ZXC'

# 配置数据库信息:实际开发，需要使用数据库的真是IP
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@127.0.0.1:3306/test01'
# 是否追踪数据库的修改：会极大的消耗数据库的性能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Author(db.Model):
    """作者模型类：一，一个作者可以有多本书"""

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    books = db.relationship('Book', backref='author', lazy='dynamic')


class Book(db.Model):
    """作者模型类：一，一个作者可以有多本书"""

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # 外键
    author_id = db.Column(db.Integer, db.ForeignKey(Author.id))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    """删除书籍"""
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print e
            db.session.rollback()
            flash(u'删除书籍失败')
    else:
        flash(u'书籍不存在')

    # 重新刷新界面
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    # 实例化自定义表单对象
    book_form = BookForm()

    # 如果请求方法时POST，表示用户在添加书籍信息
    if request.method == 'POST':
        # 先验证表单，在保存数据信息
        if book_form.validate_on_submit():
            # 取出作者名字和书名
            # author_name = request.form.get('author')
            # book_name = request.form.get('book')
            author_name = book_form.author.data
            book_name = book_form.book.data

            # 判断传入的作者是否存在
            author = Author.query.filter(Author.name == author_name).first()
            if author:
                # 判断传入的书籍是否已存在
                book = Book.query.filter(Book.name == book_name, Book.author_id == author.id).first()
                if book:
                    # 提示用户书名已存在
                    flash(u'书名已存在')
                else:
                    # 将书籍添加到作者
                    book = Book(name=book_name, author_id=author.id)
                    # 将数据存储到数据库
                    try:
                        db.session.add(book)
                        db.session.commit()
                    except Exception as e:
                        print e
                        db.session.rollback()  # 数据库操作失败就回滚
                        flash(u'添加书籍信息到作者失败')
            else:
                # 添加新的作者
                author = Author(name=author_name)
                # 添加新的书籍
                book = Book(name=book_name)
                # 将author模型对象，赋值给Author给Book反向引用的author属性
                book.author = author

                try:
                    db.session.add(book)  # 当book.author = author 时，只需要add我们的book就可以了
                    db.session.commit()
                except Exception as e:
                    print e
                    db.session.rollback()  # 数据库操作失败就回滚
                    flash(u'添加新的书籍和作者失败')

    # 查询作者数据
    authors = Author.query.all()

    return render_template('test02_bookmanager.html', form=book_form, authors=authors)


if __name__ == '__main__':
    # 每次在建表前，删除测试的数据,为了保证下此测试时数据时全新的，没有实际意义
    db.drop_all()
    db.create_all()

    # 准备测试数据
    au1 = Author(name='老王')
    au2 = Author(name='老尹')
    au3 = Author(name='老刘')
    # 把数据提交给用户会话
    db.session.add_all([au1, au2, au3])
    # 提交会话
    db.session.commit()
    bk1 = Book(name='老王回忆录', author_id=au1.id)
    bk2 = Book(name='我读书少，你别骗我', author_id=au1.id)
    bk3 = Book(name='如何才能让自己更骚', author_id=au2.id)
    bk4 = Book(name='怎样征服美丽少女', author_id=au3.id)
    bk5 = Book(name='如何征服英俊少男', author_id=au3.id)
    # 把数据提交给用户会话
    db.session.add_all([bk1, bk2, bk3, bk4, bk5])
    # 提交会话
    db.session.commit()

    app.run(debug=True)
