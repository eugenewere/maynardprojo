

    function randomStr(len, arr) {
    var ans = '';
    for (var i = len; i > 0; i--) {
        ans += arr[Math.floor(Math.random() * arr.length)];
    }
    return ans;
    }

    function setCookie(cname, cvalue, exdays) {
      var d = new Date();
      d.setTime(d.getTime() + (exdays*24*60*60*1000));
      var expires = "expires="+ d.toUTCString();

      document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    }

    function checkCookie() {
      var user = getCookie("Mashkys");
      if (user !== "") {
          var cookie1s = document.getElementsByClassName('cookie1');

          for (i=0; i<cookie1s.length; i++){
              cookie1s[i].setAttribute('value', user);
          }


      } else {
            var name = "Mashkys";
            var new_value = randomStr(32, 'abcdefgh123456789');
            setCookie(name, new_value, 32);

      }
    }

    function getCookie(cname) {
      var name = cname + "=";
      var ca = document.cookie.split(';');
      for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
          return c.substring(name.length, c.length);
        }
      }
      return "";
    }

    setInterval(checkCookie,100);

    function sendcookie() {
         var user = getCookie("Mashkys");
         return user

    }
