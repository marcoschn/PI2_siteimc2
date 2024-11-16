from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb

from data import data_loader

import MySQLdb.cursors
import re




app=Flask(__name__)


app.secret_key = 'passpi2univesp'

app.config['MYSQL_HOST'] = '145.223.31.145'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'UnivPi0811!'
app.config['MYSQL_DB'] = 'univespi2'

mysql = MySQL(app)

#carregando grafico
data_loader_obj = data_loader.DataLoader()
DATA_SET_FULL = data_loader_obj.prepare_data_set_full()
DATA_SET_GROUPED = data_loader_obj.prepare_data_set_grouped()
#fim


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


@app.route('/perfil', methods =['GET', 'POST'])
def perfil():
    if session['loggedin'] == True:
            sqlusuario="""SELECT 
            dadosusuario.nome as nomecompleto, 
            DATE_FORMAT(dadosusuario.dtnascimento, '%Y-%m-%d') as dtnasc, 
            usuarios.codusuario as idusuario, 
            usuarios.nome as nome, 
            usuarios.email as email  ,
            usuarios.senha as senha
            FROM univespi2.usuarios 
            inner JOIN univespi2.dadosusuario  
            ON usuarios.codusuario = dadosusuario.codusuario 
            WHERE usuarios.codusuario = """ + str(session['id'])
            print(sqlusuario)

            cursorperfil = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursorperfil.execute(sqlusuario)
            perfilusuario = cursorperfil.fetchall()
            print(perfilusuario)
            return render_template('perfil.html', perfilusuario=perfilusuario[0])
    else:
        return redirect(url_for('index'))

@app.route('/atualizaperfil', methods =['GET', 'POST'])
def atualizaperfil():
    if session['loggedin'] == True:
        if request.method == 'POST':
            usuario= request.form['nomeusuario']
            usuarioinicial=request.form['usuarioinicial']
            emailinicial=request.form['emailinicial']
            email = request.form['emailusuario']
            nomecompleto = request.form['nomecompleto']
            dtnascimento = request.form['dtnasc']
            senha=request.form['senha']
            senharepita = request.form['senharepita']
            if usuario != usuarioinicial:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM usuarios WHERE nome = % s', (usuario,))
                account = cursor.fetchone()
                if account:
                    problemausuario = 1
                else:
                    problemausuario = 0
            else:
                problemausuario = 0

            if email != emailinicial:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM usuarios WHERE nome = % s', (usuario,))
                emailusu = cursor.fetchone()
                if emailusu:
                    problemaemail = 1
                else:
                    problemaemail = 0
            else:
                problemaemail = 0

            if senha != senharepita:
                problemasenha= 1
            else:
                problemasenha= 0

            resultado = problemausuario + problemaemail + problemasenha
            print("resultado:" + str(resultado))
            print(usuario)
            print(usuarioinicial)
            print(nomecompleto)
            print(dtnascimento)
            print(email)
            print(emailinicial)
            print(senha)
            print(senharepita)
            if resultado == 0:
                cursorregistros = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                sqlatualizaperfil="UPDATE dadosusuario SET nome = '" + nomecompleto + "', dtnascimento='" + dtnascimento + "' where codusuario=" + str(session['id'])
                cursorregistros.execute(sqlatualizaperfil)
                sqlatualizausuario = "UPDATE usuarios SET nome = '" + usuario + "', email='" + email + "', senha='" + senha + "' where codusuario=" + str(session['id'])
                cursorregistros.execute(sqlatualizausuario)
                mysql.connection.commit()
                flash('Perfil atualizado.')
                return redirect(url_for('home'))
            else:
                if problemausuario==1:
                    flash('Esse usuario já existe. Digite outro nome de usuário')
                if problemasenha==1:
                    flash('As senhas não são iguais. Por favor, confirme corretamente sua senha.')
                if problemaemail==1:
                    flash('Esse email já está sendo utilizado por alguém. Por favor, escolha outro.')
                #return redirect(url_for('home'))
                return redirect(request.referrer)

    else:
        return redirect(url_for('index'))

@app.route('/grafico', methods=['GET', 'POST'])
def grafico():
    """
    the main route rendering index.html
    :return:
    """

    labels = [x[0] for x in DATA_SET_GROUPED]
    values_confirmed = [x[1] for x in DATA_SET_GROUPED]
    values_deaths = [x[2] for x in DATA_SET_GROUPED]
    values_recovered = [x[3] for x in DATA_SET_GROUPED]

    return render_template('grafico.html', template_labels=labels,
                           template_values_confirmed=values_confirmed,
                           template_values_deaths=values_deaths,
                           template_values_recovered=values_recovered)



@app.route('/<string:item>', methods=['GET'])
def get_item_details(item):
    """
    the route for each "drilldown" item details
    :param item:
    :return:
    """
    filtered_data_set = [x for x in DATA_SET_FULL if x.get('ObservationDate') == item]

    return render_template('details.html', template_data_set=filtered_data_set)

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

        if password == passwordconf :
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM usuarios WHERE email = % s', (email, ))
            account = cursor.fetchone()
            if account:
                msg = 'Esse email já está cadastrado. Use outro'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Email inválido'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Nome deve conter apenas letras e números !'
            elif not username or not password or not email:
                msg = 'Por favor, preencha seus dados!'
            else:
                cursor.execute('INSERT INTO usuarios VALUES (NULL, % s, % s, % s)', (email, password, username, ))
                cursor.execute('select last_insert_id() from usuarios')
                idusuario=cursor.lastrowid
                #print(idusuario)
                sqlinsertdados="INSERT INTO dadosusuario VALUES (" + str(idusuario) + ", '" + username + "', '1900-01-01')"
                #print(sqlinsertdados)
                cursor.execute(sqlinsertdados)
                mysql.connection.commit()
                msg = 'Usuário cadastrado com sucesso!'
                #return render_template('registrar.html', msg=msg)
                return render_template("index.html")
        else :
            msg = 'As senhas não estão iguais'
    elif request.method == 'POST':
        msg = 'Por favor, preencha os dados'
    return render_template('registrar.html', msg = msg)


if __name__ == "__main__":
    app.run(debug=True)
