from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb

import MySQLdb.cursors
import re




app=Flask(__name__)


app.secret_key = 'passpi2univesp'

app.config['MYSQL_HOST'] = '145.223.31.145'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'UnivPi0811!'
app.config['MYSQL_DB'] = 'univespi2'

mysql = MySQL(app)

@app.route("/")
def index():
    session['loggedin'] = False
    return render_template("index.html")

@app.route('/login', methods =['GET', 'POST'])
def login():
    session['loggedin'] = False
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        username = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE email = % s AND senha = % s', (username, password, ))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['codusuario']
            session['username'] = account['nome']
            session['email'] = account['email']
            msg = 'Logado com sucesso!'
            return redirect(url_for('home'))
        else:
            msg = 'Email ou senha incorretos'
    return render_template('login.html', msg = msg)

@app.route('/home', methods=['GET', 'POST'])
def home():
    if session['loggedin'] == True:
        bemvindo = 'Bem-vindo(a), ' + session['username'] + '!'
        cursorregistros = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = """
                        select 
        	                registros.codregistro as id, 
        	                date_format(registros.dtregistro,'%%d/%%m/%%Y') as dataregistro, 
        	                registros.alturam, 
        	                registros.pesokg, 
        	                format(((pesokg) / ((alturam)*(alturam))),1) as imc, 
        	                (case
        		                when (pesokg)/((alturam)*(alturam)) < 18.5 then 'baixo peso' 
        		                when (pesokg)/((alturam)*(alturam)) >=18.5 and (pesokg)/((alturam)*(alturam)) < 25 then 'normal' 
        		                when (pesokg)/((alturam)*(alturam)) >=25 and (pesokg)/((alturam)*(alturam)) < 30 then 'sobrepeso' 
        		                when (pesokg)/((alturam)*(alturam)) >=30 and (pesokg)/((alturam)*(alturam)) < 35 then 'obesidade classe I' 
        		                when (pesokg)/((alturam)*(alturam)) >=35 and (pesokg)/((alturam)*(alturam)) < 40 then 'obesidade classe II' 
        		                when (pesokg)/((alturam)*(alturam)) >=40 then 'obesidade classe III' 
        		                else '0'
        	                end) as status
                        from 
        	                univespi2.registros 
                        inner join univespi2.usuarios on registros.regcodusuario = usuarios.codusuario
                        where 
        	                registros.regcodusuario = % s 
                        order by 
        	            dtregistro desc
                    """
        cursorregistros.execute(sql, (session['id'],))
        resultados = cursorregistros.fetchall()
        # for rows in resultados:
        #    print(rows)
        return render_template('home.html', bemvindo=bemvindo, resultados=resultados)
    return redirect(url_for('login'))



@app.route('/add_registro', methods=['GET', 'POST'])
def add_registro():
    if session['loggedin'] == True:
        #conn = mysql.connect()
        #cur = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            dtregistro = request.form['dtregistro']
            alturam = request.form['alturam']
            pesokg = request.form['pesokg']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO registros VALUES (NULL, % s, % s, % s, % s)',
                           (pesokg, alturam, dtregistro, session['id'],))
            mysql.connection.commit()
            flash('Medição adicionada com sucesso')

            return redirect(url_for('home'))

    else:
        return redirect(url_for('index'))


@app.route('/edit/<id>', methods=['POST', 'GET'])
def get_medicao(id):
    #print(id)
    if session['loggedin'] == True:
        querysql="select codregistro, DATE_FORMAT(dtregistro, '%Y-%m-%d') as dt, alturam, pesokg from univespi2.registros where codregistro=" + id
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(querysql)
        data = cursor.fetchall()

        cursor.close()
        print(data[0])
        return render_template('edit.html', registro=data[0])
    else:
        return redirect(url_for('index'))

@app.route('/update/<id>', methods=['POST'])
def update_medicao(id):
    if session['loggedin'] == True:
        if request.method == 'POST':
            dtregistro = request.form['dtregistro']
            pesokg = request.form['pesokg']
            alturam = request.form['alturam']

            bemvindo = 'Bem-vindo(a), ' + session['username'] + '!'
            cursorregistros = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursorregistros.execute("""
                UPDATE registros
                SET dtregistro = %s,
                    pesokg = %s,
                    alturam = %s
                WHERE codregistro = %s
            """, (dtregistro, pesokg, alturam, id))
            mysql.connection.commit()
            flash('Registro atualizado.')

            return redirect(url_for('home'))
    else:
        return redirect(url_for('index'))


@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete_employee(id):
    if session['loggedin'] == True:
        querysql = "delete from registros where codregistro=" + id
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(querysql)
        mysql.connection.commit()
        flash('Medição removida.')

        return redirect(url_for('home'))

    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/registrar', methods =['GET', 'POST'])
def registrar():
    msg = ''
    if request.method == 'POST' and 'nome' in request.form and 'password' in request.form and 'passwordconf' in request.form and 'email' in request.form :
        username = request.form['nome']
        password = request.form['password']
        passwordconf = request.form['passwordconf']
        email = request.form['email']
        print(username)
        print(password)
        print(email)
        print(passwordconf)
        if password == passwordconf :
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM usuarios WHERE email = % s', (email, ))
            account = cursor.fetchone()
            if account:
                msg = 'Esse email já está cadastrado'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Email inválido'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Nome deve conter apenas letras e números !'
            elif not username or not password or not email:
                msg = 'Por favor, preencha seus dados!'
            else:
                cursor.execute('INSERT INTO usuarios VALUES (NULL, % s, % s, % s)', (email, password, username, ))
                mysql.connection.commit()
                msg = 'Usuário cadastrado com sucesso!'
                return render_template('registrar.html', msg=msg)
                #return render_template("index.html")
        else :
            msg = 'As senhas não estão iguais'
    elif request.method == 'POST':
        msg = 'Por favor, preencha os dados'
    return render_template('registrar.html', msg = msg)


@app.route("/inserir", methods =['GET', 'POST'])
def inserir():
    if session['loggedin'] == True:
        bemvindo = ''
        msg = ''
        if request.method == 'POST' and 'altura' in request.form and 'peso' in request.form and 'dt' in request.form:
            altura = request.form['altura']
            peso = request.form['peso']
            dt = request.form['dt']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO registros VALUES (NULL, % s, % s, % s, % s)', (peso, altura, dt, session['id'],))
            mysql.connection.commit()
            msg = 'Dados inseridos com sucesso!'
            bemvindo = 'Bem-vindo(a), ' + session['username'] + '!'
            cursorregistros = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = """
                            select 
            	                codregistro as id,
            	                date_format(registros.dtregistro,'%%d/%%m/%%Y') as dataregistro, 
            	                registros.alturam, 
            	                registros.pesokg, 
            	                format(((pesokg) / ((alturam)*(alturam))),1) as imc, 
            	                (case
            		                when (pesokg)/((alturam)*(alturam)) < 18.5 then 'baixo peso' 
            		                when (pesokg)/((alturam)*(alturam)) >=18.5 and (pesokg)/((alturam)*(alturam)) < 25 then 'normal' 
            		                when (pesokg)/((alturam)*(alturam)) >=25 and (pesokg)/((alturam)*(alturam)) < 30 then 'sobrepeso' 
            		                when (pesokg)/((alturam)*(alturam)) >=30 and (pesokg)/((alturam)*(alturam)) < 35 then 'obesidade classe I' 
            		                when (pesokg)/((alturam)*(alturam)) >=35 and (pesokg)/((alturam)*(alturam)) < 40 then 'obesidade classe II' 
            		                when (pesokg)/((alturam)*(alturam)) >=40 then 'obesidade classe III' 
            		                else '0'
            	                end) as status
                            from 
            	                piunivespimc.registros 
                            inner join piunivespimc.usuarios on registros.regcodusuario = usuarios.codusuario
                            where 
            	                registros.regcodusuario = % s 
                            order by 
            	            dtregistro desc
                        """
            cursorregistros.execute(sql, (session['id'],))
            resultados = cursorregistros.fetchall()

            return render_template('home.html', bemvindo=bemvindo , resultados=resultados)
        return render_template('inserir.html', msg = msg)

    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
