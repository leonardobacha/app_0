Esse é um aplicativo com rotas de rios, coletas e parametros utilizando a tecnologia FASTAPI Python.

É bom notar que neste caso, não há containers, e o aplicativo deve-se conectar com o banco de dados Postgres instalado na própria máquina com usuário e senha. Neste caso está definido como fastapi_user e ...
Ainda deve-se inserir o arquivo init no banco de dados. 

Para fazer rodar deve-se entrar no diretorio do app e inserir o comando: python -m uvicorn main:app --reload
Instalar o requiremnets.txt tambem com: python pip install -r requirements.txt

Esta API serve de base para o front mobile de teste app_0_react_native
