document.addEventListener("DOMContentLoaded", function () {
    let form = document.getElementById("user-input-form");
    let input = document.getElementById("user-input");

    if(form) { // Add this condition to check if the element exists before adding the event listener
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            let userMsg = input.value.trim();
            if (userMsg === "") {
                return;
            }

            input.value = "";
            appendMessage("user-msg", userMsg);

            fetch("/get", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: "msg=" + encodeURIComponent(userMsg)
            })
                .then(response => response.json())
                .then(data => {
                    appendMessage("chatbot-msg", data["response"]);
                })
                .catch(error => {
                    console.error("Error fetching chatbot response:", error);
                });
        });
    }

    function appendMessage(className, textContent) {
        let msgDiv = document.createElement("div");
        msgDiv.className = className;
        msgDiv.textContent = textContent;
        document.getElementById("chatbox").appendChild(msgDiv);
    }
});
