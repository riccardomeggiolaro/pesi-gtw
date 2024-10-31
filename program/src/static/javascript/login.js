
        let host = window.location.host
        let hostname = window.location.hostname

        let value = ('; '+document.cookie).split(`; tokenBaron=`).pop().split(';')[0];
        if(value){
            window.location.replace("http://"+host+"/dashboard.html");
        }
        let username = document.querySelector("#inputUsername")
        let password = document.querySelector("#inputPassword")
        let button = document.querySelector("#inputSumbit")
        let loginInfo = document.querySelector("#loginInfo")
        let infomachine = document.getElementById("infomachine")

        window.onload = function(){
        		let urlinfomachine = "http://"+hostname+":8000/infomachinelogin"
		        fetch(urlinfomachine)
		        .then(response => response.json())
		        .then(json => {
			        infomachine.textContent = "Firmware: " + json.firmware + " | Model name: " + json.model_name + " | Serial number: " + json.serial_number
			        console.log(json)
		        })
		        body.classList.remove("displayNone")
        }

        button.onclick = () => {
            if(username.value != "" && password.value != ""){
                loginInfo.classList.toggle("displayNone")
                let url = "http://"+hostname+":8000/login/" + username.value + "/" + password.value 
                fetch(url)
                .then(response => response.json())
                .then(json => {
				    if(json.token != undefined){
						let now = new Date()
						now.setDate(now.getDate()+2)
						expire = now.toUTCString()
                        document.cookie = "tokenBaron="+json.token + "; expires=" + expire
                        window.location.replace("http://"+host+"/dashboard.html");
                    }else{
                        loginInfo.classList.remove("displayNone")
                        loginInfo.textContent = "Username o password non validi"
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                });
            }else{
                loginInfo.classList.remove("displayNone")
                if(username.value == "" && password.value == ""){
                    loginInfo.textContent = "Inserisci lo username e la password"
                }else if(username.value == "" && password.value != ""){
                    loginInfo.textContent = "Inserisci lo username"
                }else if(username.value != "" && password.value == ""){
                    loginInfo.textContent = "Inserisci la password"
                }
            }
        }



