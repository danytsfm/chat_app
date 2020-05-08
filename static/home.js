if(!localStorage.getItem('messages'))
   localStorage.setItem('messages', []);
var current_channel;

document.addEventListener('DOMContentLoaded', () => {
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  socket.on('connect', () => {

    current_channel = document.querySelector('#cha').innerHTML;
    document.querySelector('#messages').innerHTML = localStorage.getItem(['messages' + current_channel]);

    // document.querySelector('#send').disabled = true;

     document.querySelector('#input-default').onkeyup = () =>{
      if(document.querySelector('#input-default').value.length < 0)
         ('keydown',function(e){if(e.keyIdentifier=='U+000A'||e.keyIdentifier=='Enter'||e.keyCode==13)
         {e.preventDefault();return false;}},true);
      // document.querySelector('#send').disabled = false;
    //   // else {
    //     // document.querySelector('#send').disabled = true;
      };
    // };

    document.querySelector('#callmodal').onclick = function(){
      document.querySelector('#newChannel').onkeyup = () =>{
        if(document.querySelector('#newChannel').value.length < 0)
        document.querySelector('#saveChannel').disabled = true;
        else {
          document.querySelector('#saveChannel').disabled = false;
        };
      };
      document.querySelector('#staticBackdrop').style.display = 'block';
    };

    document.querySelector('#modalclose').onclick = function() {
      document.querySelector('#newChannel').value = '';
      document.querySelector('#staticBackdrop').style.display = 'none';
    };

    document.querySelector('#callmodalContact').onclick = function(){
      document.querySelector('#staticContact').style.display = 'block';
    };

    document.querySelector('#modalContactclose').onclick = function() {
      document.querySelector('#addContact').value = '';
      document.querySelector('#staticContact').style.display = 'none';
    };

    document.querySelector('#saveChannel').onclick = function(){
      const channel ='@'+ document.querySelector('#newChannel').value;
      document.querySelector('#newChannel').value = '';
      socket.emit('flask_bridge', channel, 'channel');
      document.querySelector('#staticBackdrop').style.display = 'none';
    };

    document.querySelector('#saveContact').onclick = function(){
      const person = document.querySelector('#addContact').value;
      document.querySelector('#addContact').value = '';
      socket.emit('flask_bridge', person, 'adduser');
      document.querySelector('#staticContact').style.display = 'none';
    };


    document.querySelector('#handle_messages').onsubmit = () =>{
      // assign the txt value to const msg
      const msg = document.querySelector('#input-default').value;
      // clear the txtMessage
      document.querySelector('#input-default').value = '';
      // send message to socket
      socket.emit('submit messages', {'new_msg': msg});
      return false;
    };


    document.querySelectorAll('#channels').forEach(function(button){
      document.querySelectorAll('.btnChannels').forEach(function(button) {
        button.onclick = function(){
          socket.emit('flask_bridge', button.innerHTML,  'switch_channel')
        }

      });

    });

// this is the end of the socket on

});



   socket.on('redirect', data =>{
     window.location = `${data.destination}`;

  //   const btn = document.createElement('button');
  //   btn.innerHTML = '@'+`${data.new_channel}` ;
  //   btn.id = `${data.new_channel}`;
  //   btn.className = 'btnChannels';
  //   document.querySelector('#channels').append(btn);
  //   channels = document.querySelector('#channels').innerHTML;
  //   localStorage.setItem('channels', channels);
   });

  socket.on('announce message' , data => {
    const div = document.createElement('div');
    div.innerHTML = '<b>'+`${data.display_name}`+'</b>' + '   '+ '<small>'+`${data.local}`+'</small>' + '<br>' +`${data.new_msg}` ;
    window.current_channel = `${data.channel}`
      // add na message  lista
    document.querySelector('#messages').prepend(div);
    messages = document.querySelector('#messages').innerHTML;
// save previous msg to local storage
    localStorage.setItem(['messages' + window.current_channel], messages);
  });


});
