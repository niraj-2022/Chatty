let wsStart = 'ws://'
let loc = window.location
let endpoint = wsStart + loc.host + loc.pathname

if (loc.protocol === 'https') {
    wsStart = 'wss://'
}

console.log(endpoint)
var socket = new WebSocket(endpoint)

socket.onopen = async function (e) {
    console.log('open', e)
    let message = document.getElementById('message')
    let submit_btn = document.getElementById('submit_btn')
    let sender = document.getElementById('sender')

    $(document).on('submit', '#message-form', function (e) {
        e.preventDefault();
        console.log("HI FROM NEW")
        let receiver = document.getElementById('receiver')

        let data = {
            'message': message.value,
            'sender': sender.value,
            'receiver': receiver.value
        }

        data = JSON.stringify(data)
        socket.send(data)
        document.getElementById('message-form').reset()
    })
}

socket.onmessage = async function (e) {
    console.log('Message Received', e)
    let data = JSON.parse(e.data)
    let message = data['message']
    console.log('[MESSAGE]: ', data)

    let sender = document.getElementById('sender')
    let receiver = document.getElementById('receiver')

    if (data['sender'] != sender.value && data['sender'] != receiver.value)
        return

    let chat_block = document.getElementById("chat-block")

    var div = document.createElement('div')
    var para = document.createElement('p')
    para.innerText = message
    para.className = "chat-msg"
    div.className = "chat-bubble"

    console.log(sender.value, data['sender'])

    if (sender.value === data['sender']) {
        div.style = "text-align: right;"
        para.style = "background-color: #3381ff; border-bottom-right-radius: 0;"
    }
    else {
        para.style = "background-color: #363d47; border-bottom-left-radius: 0;"
    }

    div.appendChild(para)
    chat_block.appendChild(div)
}

socket.onerror = async function (e) {
    console.log('[ERROR] ', e)
}

socket.onclose = async function (e) {
    console.log('[CONNECTION CLOSED]', e)
}

$(document).on('submit', '#add_friend', function (e) {
    e.preventDefault();

    $.ajax({
        type: 'POST',
        url: '/addfriend',
        data: {
            me: $('#me').val(),
            friend: $('#friend').val(),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        sucess: function () { }
    });

    document.getElementById('add_friend').reset()
})