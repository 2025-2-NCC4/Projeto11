const express = require('express');
const mysql = require('mysql2');
const bodyParser = require('body-parser');
const path = require('path');
const cors = require('cors')
const multer = require('multer');
const fs = require('fs');

// Set up multer storage (optional: save to disk or keep in memory)

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, path.join(__dirname, 'uploads')); // save to /uploads directory
    },
    filename: function (req, file, cb) {
        // Save the file with original name (or customize)
        cb(null, file.originalname);
    }
});
const upload = multer({ storage: storage });

const app = express();
const port = process.env.PORT || 5000;

app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' })); // Increased body size limit
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

// Conexão MySQL
const db = mysql.createConnection({
  host: 'localhost',
  user: 'iury', 
  password: 'xaviersqliury2910', 
  database: 'dashboard',
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
    var cargo = req.body.cargo;

    var query = 'INSERT INTO usuario (NOME, EMAIL, SENHA, CARGO) VALUES (?,?,?,?)'
    db.query(query, [nome, email, senha, cargo], (err, result) =>{
        if (err){
            console.error('Falha ao adicionar o usuario', err)
            return res.status(500).json({ error: 'Falha ao adicionar usuario' + err.message });
        }
        res.status(201).json({message: 'Usuario Adicionado!'})
    })
})

app.post("/login", function (req, res){
  var email = req.body.email;
  var senha = req.body.senha;

  var query1 = 'Select * from usuario where email = ?';
  db.query(query1, [email], (err, result)=>{
    if(err){
        console.error('Erro ao procurar usuario', err)
        return res.status(500).json({ error: 'Email não encontrado' + err.message });
    }
      if (result.length === 0) {
          return res.status(404).json({ error: 'Usuario não encontrado' });
      }
    if(result[0].senha === senha){
      var userData = {
          nome: result[0].nome,
          cargo: result[0].cargo
      }
      res.status(201).json(userData);
    }else{
      return res.status(404).json({ error: 'Senha Incorreta' })
    }
  })
})

app.post('/upload_csv', upload.single('file'), (req, res) => {
    try {
        const file = req.file;
        const nome = req.body.nome;
        const base = req.body.base;
        const ano = req.body.ano;
        const mes = req.body.mes;

        if (!file || !nome || !base) {
            return res.status(400).json({ error: "Missing file or form data." });
        }

        var queryNome = 'select * from usuario where nome = ?';

        db.query(queryNome, [nome], (err, result)=>{
          if(err){
            console.error("Erro ao procurar o usuário")
            return res.status(500).json({ error: 'Erro ao procurar o usuário' + err.message });
          }
          if (result.length === 0) {
            console.error("Usuário não encontrado")
            return res.status(500).json({ error: 'Usuário não encontrado' + err.message });
          }
          var id = result[0].id

          var queryWrite = 'Insert into csv(titulo, caminho, tipoBase, idUsuario, ano, mes) values(?,?,?,?,?,?)';

          db.query(queryWrite, [file.originalname, `./uploads/${file.originalname}`, base, id, ano, mes], (err, result)=>{
            if(err){
            console.error("Erro na comunicação")
            return res.status(500).json({ error: 'Erro na comunicação' + err.message });
          }
          return res.status(200).json({ message: 'CSV recebido com sucesso!' });
          
          })
        })
    } catch (err) {
        console.error("Erro ao processar upload:", err);
        res.status(500).json({ error: "Erro ao processar o upload." });
    }
});

app.get('/get_csv', function(req, res){
  query = 'Select * from csv';

  db.query(query,(err,result)=>{
    if(err){
      console.log("Erro ao buscar as informações", err)
      return res.status(500).json({erro: "Erro ao buscar as informações" + err})
    }
    return res.status(200).json(result)
  })
})

app.post('/mudar_informacoes', function(req, res){
  const nome = req.body.nome;
  const nomeAnterior = req.body.nomeanterior;
  const email = req.body.email;
  const senhaAntiga = req.body.senhaantiga;
  const senhaNova = req.body.senhanova;

  const query = 'Select * from usuario where nome = ?'

  db.query(query, [nome], (err, result)=>{
    if(err){
      console.log("Erro ao encontrar usuário", err)
      return res.status(500).json({erro: "Erro ao encontrar usuário" + err})
    }
    const id = result[0].id;
    const senha = result[0].senha;
    if(senha != senhaAntiga){
      return res.status(400).json({erro: "Senha incorreta"})
    }
    if(senhaNova === ""){
      const query1 = 'Update usuario set nome = ?, email = ? where id = ?'
      db.query(query1,[nome, email, id], (err, result)=>{
      if(err){
      console.log("Erro ao atualizar as informações", err)
      return res.status(500).json({erro: "Erro ao atualizar as informações" + err})
    }
    return res.status(200).json({ message: 'Dados atualizados com sucesso' });
  })
    }else{
      const query1 = 'Update usuario set nome = ?, email = ?, senha = ? where id = ?'
      db.query(query1,[nome, email, senhaNova, id], (err, result)=>{
    if(err){
      console.log("Erro ao atualizar as informações", err)
      return res.status(500).json({erro: "Erro ao atualizar as informações" + err})
    }
    return res.status(200).json({ message: 'Dados atualizados com sucesso' });
  })
    }
  })

  
})

// Inicializar o Servidor
app.listen(port, () => {
  console.log(`Server running on ${port}`);
});