const API_URL = "http://192.168.1.10:8000";
let currentUser = "";
let sessionTicket = "";

async function register() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const msg = document.getElementById("msg");

    try {
        const response = await fetch(`${API_URL}/register?username=${encodeURIComponent(user)}&password=${encodeURIComponent(pass)}`, {
            method: "POST"
        });
        const data = await response.json();
        
        if (response.ok) {
            msg.style.color = "#4CAF50";
            msg.innerText = data.message;
        } else {
            msg.style.color = "#f44336";
            msg.innerText = data.detail || "Błąd rejestracji";
        }
    } catch (err) {
        msg.style.color = "#f44336";
        msg.innerText = "Błąd połączenia z serwerem!";
    }
}

async function login() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const msg = document.getElementById("msg");

    try {
        const response = await fetch(`${API_URL}/login?username=${encodeURIComponent(user)}&password=${encodeURIComponent(pass)}`, {
            method: "POST"
        });
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            sessionTicket = data.ticket; // Zapamiętujemy ticket ze zwróconej odpowiedzi

            document.getElementById("auth-container").classList.add("hidden");
            document.getElementById("dashboard-container").classList.remove("hidden");
            document.getElementById("user-display").innerText = data.user;
            
            loadAchievements(data.user);
        } else {
            msg.style.color = "#f44336";
            msg.innerText = data.detail || "Błędny login lub hasło";
        }
    } catch (err) {
        msg.style.color = "#f44336";
        msg.innerText = "Błąd połączenia z serwerem!";
    }
}

async function loadAchievements(username) {
    const listContainer = document.getElementById("achievements-list");
    listContainer.innerHTML = "<li>Ładowanie osiągnięć...</li>";

    try {
        const response = await fetch(`${API_URL}/user-achievements/${encodeURIComponent(username)}`);
        const data = await response.json();

        if (response.ok) {
            listContainer.innerHTML = "";
            
            if (data.achievements.length === 0) {
                listContainer.innerHTML = "<li>Brak zdobytych osiągnięć</li>";
                return;
            }

            data.achievements.forEach(ach => {
                const li = document.createElement("li");
                li.innerHTML = `🏆 <b>${ach.name}</b> — Punkty: <b>${ach.total_score ?? 0}</b> (Speedrun: ${ach.is_speedrun ? "Tak" : "Nie"})`;
                listContainer.appendChild(li);
            });
        } else {
            listContainer.innerHTML = "<li>Nie udało się pobrać osiągnięć</li>";
        }
    } catch (err) {
        listContainer.innerHTML = "<li>Błąd połączenia z serwerem</li>";
    }
}

function logout() {
    currentUser = "";
    sessionTicket = "";
    document.getElementById("dashboard-container").classList.add("hidden");
    document.getElementById("auth-container").classList.remove("hidden");
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    document.getElementById("msg").innerText = "";
    document.getElementById("achievements-list").innerHTML = "<li>Brak zdobytych osiągnięć</li>";
}

function launchVR() {
    if (!sessionTicket) {
        alert("Błąd: Brak aktywnego ticketu sesji!");
        return;
    }
    // Przekazujemy w linku wyłącznie anonimowy ticket zamiast jawnego loginu
    window.location.href = `game.html?ticket=${encodeURIComponent(sessionTicket)}`;
}