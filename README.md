# Projeto PataCheia

Este projeto utiliza um Raspberry Pi para monitoramento de animais através de visão computacional e controle de hardware, com integração a um sistema de armazenamento no Firebase. Quando um animal (como cães ou gatos) é detectado, o sistema tira uma foto, a converte para base64, e a envia para o Firebase Firestore. Além disso, o projeto inclui controle de motor via GPIO e comunicação via MQTT.

## Funcionalidades

- **Detecção de animais**: Utiliza o modelo MobileNet SSD para identificar animais como cães e gatos.
- **Armazenamento no Firebase**: Salva as fotos capturadas e informações relacionadas no Firebase Firestore, incluindo a imagem em base64.
- **Controle de motor**: Aciona um motor usando GPIO do Raspberry Pi.
- **Comunicação MQTT**: O sistema se conecta a um broker MQTT para receber comandos de controle.

## Requisitos

Antes de executar o código, é necessário configurar o ambiente e as dependências:

### Hardware
- Raspberry Pi com câmera (para captura de fotos).
- Motor controlado via GPIO.
- Acesso à internet para comunicação com o Firebase e broker MQTT.

### Software
- Python 3.x
- Bibliotecas:
  - `gpiozero`
  - `opencv-python`
  - `firebase-admin`
  - `paho-mqtt`
  - `time`, `sys`, `os`, `base64`, `cv2`, `threading`, `datetime`

### Configuração do Firebase
1. Crie um projeto no Firebase.
2. Baixe o arquivo `google-services.json` do Firebase e coloque-o na pasta do projeto.
3. Altere o código com a URL do seu projeto no Firebase (em `firebase_url`).

## Instalação das Dependências

Para instalar as bibliotecas necessárias, execute os seguintes comandos:

```bash
pip install gpiozero opencv-python firebase-admin paho-mqtt
```

## Como Executar o Projeto

### Passo 1: Configuração Firebase
1. Coloque o arquivo `google-services.json` na pasta do seu projeto.
2. Ajuste a URL do Firebase no código para o seu projeto.

### Passo 2: Executar o Script

Com as dependências instaladas e a configuração do Firebase pronta, você pode executar o script:

```bash
python main.py
```

### Passo 3: Funcionamento

- O script inicia a detecção de animais com a câmera conectada ao Raspberry Pi.
- Sempre que um animal (como um cão ou gato) é detectado, a foto é salva no Firebase.
- O sistema também espera por mensagens MQTT, podendo controlar o motor conforme comandos recebidos.

## Como o Sistema Funciona

1. **Detecção de Animais**:
   - A câmera é configurada para capturar imagens.
   - O modelo MobileNet SSD é utilizado para identificar se um animal (cão ou gato) está presente.
   - Quando detectado, a imagem é salva localmente, convertida em base64 e enviada para o Firebase Firestore.

2. **Controle do Motor**:
   - O motor é controlado por GPIO usando o Raspberry Pi.
   - A sequência de passos para o motor é gerenciada por um conjunto de pinos configurados no código.

3. **Integração MQTT**:
   - O sistema se conecta ao broker MQTT para receber comandos e pode controlar dispositivos, como o motor, baseados nessas mensagens.

4. **Armazenamento no Firebase**:
   - A foto capturada é convertida para base64 e armazenada junto com a hora da captura e outros dados no Firebase Firestore.

## Licença

Este projeto está licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT).


