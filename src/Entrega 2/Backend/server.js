const express = require('express');
const mysql = require('mysql2');

const app = express();
const port = process.env.PORT || 5000;

// Conexão MySQL
const db = mysql.createConnection({
  host: '',
  user: '', 
  password: '', 
  database: '',
  ssl:{
    rejectUnauthorized: false
}
});

db.connect((err) => {
  if (err) {
    console.error('Erro ao conectar a database', err);
    return;
  }
  console.log('Conectado a Database MySQL');
});

app.use(express.json()); // Json para POST

app.post("/cadastro", function (req, res){
    var nome = req.body.nome;
    var email = req.body.email;
    var senha = req.body.senha;

    var query = 'INSERT INTO usuario (NOME, EMAIL, SENHA) VALUES (?,?,?)'
    db.query(query, [nome, email, senha], (err, result) =>{
        if (err){
            console.error('Falha ao adicionar o usuario', err)
            return res.status(500).json({ error: 'Falha ao adicionar usuario' + err.message });
        }
        res.status(201).json({message: 'Usuario Adicionado!'})
    })
})

// Inicializar o Servidor
app.listen(port, () => {
  console.log(`Server running on ${port}`);
});