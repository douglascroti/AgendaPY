from flask import Flask, render_template, request, redirect, session, json
from flask_session import Session
from flask_mysqldb import MySQL
from urllib.request import urlopen
from datetime import datetime

import os
import xml.etree.ElementTree as ET
import requests

import yaml
import hashlib

app = Flask(__name__)

# -------------------------------------------------------------
# leitura do arquivo que contem os parametros de conexão com o BD
#
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
# -------------------------------------------------------------

# -------------------------------------------------------------
# salvo os dados nas configurações da aplicação
#
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
# -------------------------------------------------------------

# -------------------------------------------------------------
# configurações referente a sessão que será armazenada
#
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
# -------------------------------------------------------------

# -------------------------------------------------------------
# diretorio padrão para upar as imagens
#
app.config['UPLOAD_FOLDER'] = '\\static\\imagens'
# -------------------------------------------------------------

# -------------------------------------------------------------
# repasso as configurações salvas para o Classe de Conexão / Sessão
#
mysql = MySQL(app)
Session(app)
# -------------------------------------------------------------

# -------------------ROTAS PARA A APLICAÇÃO--------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    error = False
    message = ''

    if session.get('logado') :
        if session['logado'] :
            return redirect('/index')
    else :

        session['logado'] = False
        if request.method == 'POST':
            
            # RECEBE OS DADOS QUE VEM DO FORMULARIO
            formLogin = request.form

            login = formLogin['login']
            senha = formLogin['senha']

            if login == '' or senha == '':
                error = True
                message = 'Informe corretamente os campos de autenticação'
                session['logado'] = False
                session['message_tela'] = message
            else :
                senha = hashlib.md5(senha.encode('utf-8')).hexdigest()
                str_sql = 'select * from acesso where login = \'{}\' and senha = \'{}\''.format(login, senha)
                bd = _BD()
                retLogin = bd.comandos(str_sql, True)
                
                if retLogin == None : 
                    error = True
                    message = 'Falha na autenticação dos dados'

                    session['logado'] = False
                    session['message_tela'] = message
                else :
                    retLogin = retLogin[0]
                    error = False
                    message = 'Usuario: '+retLogin[1]+' logado com sucesso!'

                    session['logado'] = True
                    session['codigo'] = retLogin[0]
                    session['usuario'] = retLogin[1]
                    session['message_tela'] = message
                    return redirect('/index')
    return render_template('login.html')
# -------------------------------------------------------------

@app.route('/index', methods=['GET', 'POST'])
def index():
    if session.get('logado') and session['logado'] :
        session['pesquisa_contato'] = ''
        pesquisa = request.args.get('parametro', default = None, type = str)
        if pesquisa == None :
            str_sql = 'select * from contato'
        else :
            session['pesquisa_contato'] = pesquisa
            str_sql = "select * from contato where nome like '%{}%' or email like '%{}%'".format(pesquisa, pesquisa)

        bd = _BD()
        retIndex = bd.comandos(str_sql, True)
        return render_template('index.html', sessao=session, contatos=retIndex)
    else :
        session.clear()
        session['message_tela'] = 'Você não esta logado. Faça Login para continuar'
        return redirect('/')
# -------------------------------------------------------------

@app.route('/index/detalhe', methods=['POST'])
def detalhe_contato():
    if session.get('logado') and session['logado'] :
        in_json = request.get_json()
        in_dump = json.dumps(in_json)
        in_parametros = json.loads(in_dump)
        str_sql = "select * from contato where codigo = {}".format(in_parametros["codigo"])

        bd = _BD()
        retorno = bd.comandos(str_sql, True)
        
        return json.dumps(retorno)
    else :
        session.clear()
        session['message_tela'] = 'Você não esta logado. Faça Login para continuar'
        return redirect('/')
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------

@app.route('/usuario', methods=['GET', 'POST'])
def usuario(): # ESSE METODO NÃO VALIDA A SESSÃO
    return render_template('usuario.html')
# -------------------------------------------------------------

@app.route('/usuario/salvar', methods=['POST'])
def usuario_salvar(): # ESSE METODO NÃO VALIDA A SESSÃO
    if request.method == 'POST':
        formCadastro = request.form
        if formCadastro['form-name'] == 'cadastro_usuario' :
            login = formCadastro.get('login')
            senha = formCadastro.get('senha')
            senha_confirma = formCadastro.get('senha_confirma')

            if senha != senha_confirma :
                session['message_tela'] = 'As senhas informadas devem ser iguais'
                return redirect('/usuario')

            senha = hashlib.md5(senha.encode('utf-8')).hexdigest()
            str_sql = 'insert into acesso (codigo, login, senha) values (0, \'{}\', \'{}\')'.format(login, senha)
            bd = _BD()
            retorno = bd.comandos(str_sql, False)
            if retorno['contador'] >= 1 : 
                session['message_tela'] = 'Usuário Cadastrado com Sucesso. Faça Login para Continuar'
                return redirect('/')
            else :
                session['message_tela'] = 'Não foi possivel salvar usuário'
                return redirect('/usuario')
            
    return redirect('/')
# -------------------------------------------------------------

@app.route('/usuario/admin', methods=['GET', 'POST'])
def usuario_adm():
    if session.get('logado') and session['logado'] :

        str_sql = 'select * from acesso'
        bd = _BD()
        retAcesso = bd.comandos(str_sql, True)

        return render_template('usuario_admin.html', sessao=session, acessos=retAcesso)
    else :
        session.clear()
        session['message_tela'] = 'Você não esta logado. Faça Login para continuar'
        return redirect('/')
# -------------------------------------------------------------

@app.route('/usuario/admin/salvar', methods=['POST'])
def usuario_admin_salvar():
    if request.method == 'POST':
        formCadastro = request.form
        if formCadastro['form-name'] == 'cadastro_usuario_admin' :
            codigo = formCadastro.get('codigo')
            login = formCadastro.get('login')
            senha = formCadastro.get('senha')
            senha = hashlib.md5(senha.encode('utf-8')).hexdigest()

            if codigo != '' :
                # ALTERA USUARIO
                str_sql = 'update acesso set login = \'{}\', senha = \'{}\' where codigo = {}'.format(login, senha, codigo)
            else : 
                # CADASTRO USUARIO
                str_sql = 'insert into acesso (codigo, login, senha) values (0, \'{}\', \'{}\')'.format(login, senha)

            bd = _BD()
            retorno = bd.comandos(str_sql, False)
            if retorno['contador'] >= 1 : 
                session['message_tela'] = 'Usuário Cadastrado/Alterado com Sucesso.'
            else :
                session['message_tela'] = 'Não foi possivel salvar/alterar usuário'
            
            return redirect('/usuario/admin')
            
    return redirect('/index')
# -------------------------------------------------------------

@app.route('/usuario/admin/remover', methods=['GET'])
def usuario_admin_remove():
    if session.get('logado') and session['logado'] :
        codigo = request.args.get('codigo', default = None, type = str)

        if codigo != None :

            if int(codigo) == int(session.get('codigo')) :
                session['message_tela'] = 'Você não pode remover seu proprio usuário'
            else :
                str_sql = 'delete from acesso where codigo = {}'.format(codigo)

                bd = _BD()
                retorno = bd.comandos(str_sql, False)
                if retorno['contador'] >= 1 : 
                    # CONTATO REMOVIDO COM SUCESSO
                    session['message_tela'] = 'Usuário removido com Sucesso'
                else :
                    # FALHA AO REMOVER CONTATO
                    session['message_tela'] = 'Falha ao remover Usuário'

        return redirect('/usuario/admin')
    else :
        session.clear()
        session['message_tela'] = 'Você não esta logado. Faça Login para continuar'
        return redirect('/')
# -------------------------------------------------------------

@app.route('/usuario/alteraSenha', methods=['POST'])
def usuario_alterar_senha():
    error = False
    mensagem = None

    if session.get('logado') and session['logado'] :
        in_json = request.get_json()
        in_dump = json.dumps(in_json)
        in_parametros = json.loads(in_dump)

        senha = in_parametros['senha']
        senha = hashlib.md5(senha.encode('utf-8')).hexdigest()
        str_sql = "update acesso set senha = \'{}\' where codigo = {}".format(senha, session.get('codigo'))

        bd = _BD()
        retorno = bd.comandos(str_sql, False)
        if retorno['contador'] >= 1 : 
            error = False
            mensagem = 'Senha alterada com Sucesso'
        else :
            error = True
            mensagem = 'Não foi possivel alterar a senha'
        
    else :
        session.clear()
        error = True
        mensagem = 'Faça Login novamete para continuar usando o Aplicativo'

    return {'error': error, 'mensagem': mensagem}
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    contato = {}
    if session.get('logado') and session['logado'] :

        parametro = request.args.get('codigo', default = None, type = str)
        if parametro != None :
            str_sql = 'select * from contato where codigo = {}'.format(parametro)
            bd = _BD()
            contato = bd.comandos(str_sql, True)

        return render_template('contato.html', contato=contato)
    else :
        session.clear()
        session['message_tela'] = 'Você não esta logado. Faça Login para continuar'
        return redirect('/')
# -------------------------------------------------------------

@app.route('/contato/api_json', methods=['GET', 'POST'])
def api_json():
    if session.get('logado') and session['logado'] :
        retorno = {}
        in_json = request.get_json()
        in_dump = json.dumps(in_json)
        in_parametros = json.loads(in_dump)
        url = urlopen("https://viacep.com.br/ws/"+in_parametros['cep']+"/json/")
        retorno = {'error' : False, 'mensagem' : '', 'data' : json.load(url)}
    else :
        retorno = {'error' : True, 'mensagem' : 'Faça Login novamete para continuar usando o Aplicativo', 'data' : {}}

    return retorno
# -------------------------------------------------------------

@app.route('/contato/api_xml', methods=['GET', 'POST'])
def api_xml():
    if session.get('logado') and session['logado'] :
        retorno = {}
        in_json = request.get_json()
        in_dump = json.dumps(in_json)
        in_parametros = json.loads(in_dump)

        url = "https://viacep.com.br/ws/"+in_parametros['cep']+"/xml/"
        header = { 'Accept': 'application/xml' }
        ret_url = requests.get(url, headers=header)
        xml =  ET.fromstring(ret_url.content)

        dados = {}
        for x in xml:
            dados[x.tag] = x.text

        retorno = {'error' : False, 'mensagem' : '', 'data' : dados}
    else :
        retorno = {'error' : True, 'mensagem' : 'Faça Login novamete para continuar usando o Aplicativo', 'data' : {}}

    return retorno
# -------------------------------------------------------------

@app.route('/contato/salvar', methods=['GET', 'POST'])
def contato_salvar():
    redireciona = '/index'
    contato = {}
    if session.get('logado') and session['logado'] :

        if request.method == 'POST' :

            formCadastro = request.form
            if formCadastro['form-name'] == 'cadastro_contato' :

                tem_anexo_atual = False
                tem_anexo = False
                avatar = None
                novo_nome_avatar = None

                if 'avatar' in request.files :
                    avatar = request.files['avatar']
                    if avatar.filename != '' :
                        print(avatar.filename)
                        tem_anexo = True
                        file_nome = avatar.filename.split('.')[0]
                        file_ext = avatar.filename.split('.')[1]
                        data_hora = datetime.now()
                        novo_nome_avatar = data_hora.strftime('%Y%m%d_%H%M%S')+'.'+file_ext
                    
                if formCadastro.get('diretorio_atual_avatar') != '' and formCadastro.get('diretorio_atual_avatar') != 'NoneNone':
                    tem_anexo_atual = True

                metodo_insert = False
                if formCadastro.get('codigo') == '' :
                    # codigo vazio INSERT #
                    metodo_insert = True
                    str_sql = "insert into contato (codigo, nome, email, fone, cep, cidade, endereco, bairro, complemento, dir_img, nome_img) values(0,"
                    str_sql += "\'{}\'".format(formCadastro.get('nome'))
                    str_sql += ",\'{}\'".format(formCadastro.get('email'))
                    str_sql += ",\'{}\'".format(formCadastro.get('fone'))
                    str_sql += ",\'{}\'".format(formCadastro.get('cep'))
                    str_sql += ",\'{}\'".format(formCadastro.get('cidade'))
                    str_sql += ",\'{}\'".format(formCadastro.get('endereco'))
                    str_sql += ",\'{}\'".format(formCadastro.get('bairro'))
                    str_sql += ",\'{}\'".format(formCadastro.get('complemento'))
                    if tem_anexo :
                        str_sql += ",\'{}\'".format('/static/imagens/')
                        str_sql += ",\'{}\'".format(novo_nome_avatar)
                    else : 
                        str_sql += ",null"
                        str_sql += ",null"
                    str_sql += ")"

                else : 

                    # codigo != de vazio UPDATE #
                    str_sql = "update contato set "
                    str_sql += "nome = \'{}\'".format(formCadastro.get('nome'))
                    str_sql += ",email = \'{}\'".format(formCadastro.get('email'))
                    str_sql += ",fone = \'{}\'".format(formCadastro.get('fone'))
                    str_sql += ",cep = \'{}\'".format(formCadastro.get('cep'))
                    str_sql += ",cidade = \'{}\'".format(formCadastro.get('cidade'))
                    str_sql += ",endereco = \'{}\'".format(formCadastro.get('endereco'))
                    str_sql += ",bairro = \'{}\'".format(formCadastro.get('bairro'))
                    str_sql += ",complemento = \'{}\'".format(formCadastro.get('complemento'))
                    if tem_anexo :
                        str_sql += ",dir_img = \'{}\'".format('/static/imagens/')
                        str_sql += ",nome_img = \'{}\'".format(novo_nome_avatar)

                    str_sql += " where codigo = {}".format(formCadastro.get('codigo'))

                bd = _BD()
                retorno = bd.comandos(str_sql, False)

                if retorno['contador'] >= 1 : 
                    error = False
                    if tem_anexo : # SE EXISTE NOVO ANEXO E O CADASTRO/ALTERAÇÃO RETORNO COM SUCESSO, SALVO O AVATAR NO DIRETORIO PADRÃO DA APLICAÇÃO #
                        basedir = os.path.abspath(os.path.dirname(__file__))
                        path = os.path.join(app.config['UPLOAD_FOLDER'], novo_nome_avatar)
                        avatar.save(basedir+path)

                        if tem_anexo_atual  and not metodo_insert : # SE EXISTE NOVO ANEXO E O CONTATO JA POSSUIA AVATAR, REMOVO DO DIRETORIO O ANTIVO AVATAR SOMENTE PARA UPDATE#
                            path_remove = basedir+formCadastro.get('diretorio_atual_avatar')
                            print('remover: ', path_remove)
                            os.unlink(path_remove)

                    mensagem = "Cadastro realizado com sucesso" if metodo_insert else "Contato alterado com sucesso"
                else :
                    error = True
                    mensagem = "Falha ao realizar Cadastro" if metodo_insert else "Falha ao alterar contato"
                    redireciona = '/contato' if metodo_insert else '/contato?codigo={}'.format(formCadastro.get('codigo'))

            session['message_tela'] = mensagem
            return redirect(redireciona)

        return redirect('/')
    else :
        session.clear()
        session['message_tela'] = 'Você não esta logado. Faça Login para continuar'
        return redirect('/')

    return redirect('/')
# -------------------------------------------------------------

@app.route('/contato/remover', methods=['GET'])
def contato_remove():
    if session.get('logado') and session['logado'] :
        codigo = request.args.get('codigo', default = None, type = str)

        if codigo != None :
            str_sql = 'delete from contato where codigo = {}'.format(codigo)

            bd = _BD()
            retorno = bd.comandos(str_sql, False)
            if retorno['contador'] >= 1 : 
                # CONTATO REMOVIDO COM SUCESSO
                session['message_tela'] = 'Contato removido com Sucesso'
            else :
                # FALHA AO REMOVER CONTATO
                session['message_tela'] = 'Falha ao remover Contato'

        return redirect('/index')
    else :
        session.clear()
        session['message_tela'] = 'Você não esta logado. Faça Login para continuar'
        return redirect('/')
    return redirect('/')
# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
# -------------------------------------------------------------

# -------------------------------------------------------------
# ------------------ CLASSE CONEXÃO BANCO DE DADOS ------------
# -------------------------------------------------------------
class _BD():
    def comandos(self, instrucao, select=False) :
        cur = mysql.connection.cursor()
        resultadoBD = None

        if select :
            print('========================================================')
            print('SELECT')
            print(instrucao)
            print('========================================================')
            resultValue = cur.execute(instrucao)
            if resultValue > 0:
                resultadoBD = cur.fetchall()
        else :
            print('========================================================')
            print('INSERT UPDATE DELETE')
            print(instrucao)
            print('========================================================')
    
            cur.execute(instrucao)
            rowCount = cur.rowcount
            mysql.connection.commit()
            resultadoBD = {'contador' : rowCount}

        cur.close()
        return resultadoBD
# -------------------------------------------------------------
# -------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
