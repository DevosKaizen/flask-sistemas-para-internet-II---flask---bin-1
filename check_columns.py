from app import db
from models import Class

# Verifique se a tabela class contém a coluna name
columns = db.inspect(Class).columns
print(columns)