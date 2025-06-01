// Frontend-logikk for NotatWeb applikasjonen
// Håndterer brukerautentisering, notatadministrasjon og admin-funksjonalitet

// Basis-URL for API-kall. Bruker relativ sti for å respektere gjeldende protokoll (HTTP/HTTPS)
const apiBaseUrl = "/api";

// Globale variabler for autentisering og brukerdata
let accessToken = null;
let currentUser = null;

// HTML-elementer for DOM-manipulasjon
const authContainer = document.getElementById("auth-container");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const registerFormContainer = document.getElementById(
  "register-form-container"
);
const showRegisterLink = document.getElementById("show-register");
const showLoginLink = document.getElementById("show-login");
const appContainer = document.getElementById("app-container");
const usernameDisplay = document.getElementById("username-display");
const logoutBtn = document.getElementById("logout-btn");
const noteForm = document.getElementById("note-form");
const notesContainer = document.getElementById("notes-container");
const adminPanel = document.getElementById("admin-panel");
const userList = document.getElementById("user-list");

// Håndtering av visning/skjuling av registreringsskjema
showRegisterLink.addEventListener("click", (e) => {
  e.preventDefault();
  registerFormContainer.style.display = "block";
  loginForm.parentElement.style.display = "none";
});

showLoginLink.addEventListener("click", (e) => {
  e.preventDefault();
  registerFormContainer.style.display = "none";
  loginForm.parentElement.style.display = "block";
});

// Håndtering av brukerregistrering
// Sender POST-forespørsel til /auth/register endepunktet
registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const brukernavn = document.getElementById("register-username").value;
  const passord = document.getElementById("register-password").value;

  const response = await fetch(`${apiBaseUrl}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brukernavn, passord }),
  });

  if (response.ok) {
    alert("Bruker opprettet! Logg inn.");
    registerForm.reset();
    registerFormContainer.style.display = "none";
    loginForm.parentElement.style.display = "block";
  } else {
    const data = await response.json();
    alert("Feil: " + data.msg);
  }
});

// Håndtering av brukerinnlogging
// Sender POST-forespørsel til /auth/login endepunktet
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const brukernavn = document.getElementById("login-username").value;
  const passord = document.getElementById("login-password").value;

  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brukernavn, passord }),
  });

  if (response.ok) {
    const data = await response.json();
    accessToken = data.access_token;
    currentUser = data.bruker;
    loginForm.reset();
    visApp();
  } else {
    const data = await response.json();
    alert("Feil: " + data.msg);
  }
});

// Viser hovedapplikasjonen etter vellykket innlogging
// Tilpasser visningen basert på brukertype (admin/vanlig bruker)
function visApp() {
  authContainer.style.display = "none";
  appContainer.style.display = "block";
  usernameDisplay.textContent = currentUser.brukernavn;

  if (currentUser.er_admin) {
    // For admin-brukere
    document.body.classList.add("admin-user");
    adminPanel.style.display = "block";

    // Rydder opp eksisterende notatelementer
    cleanupNoteElements();

    hentBrukere();
  } else {
    // For vanlige brukere
    document.body.classList.remove("admin-user");
    adminPanel.style.display = "none";

    // Gjenoppretter notat-administrasjonsseksjonen hvis den ikke eksisterer
    const existingNoteManagement = document.getElementById("note-management");
    if (!existingNoteManagement) {
      const newNoteManagement = document.createElement("div");
      newNoteManagement.id = "note-management";
      newNoteManagement.innerHTML = `
        <div class="note-form">
          <h2>Nytt notat</h2>
          <form id="note-form">
            <input type="text" id="note-title" placeholder="Tittel" required />
            <textarea id="note-content" placeholder="Notatinnhold" required></textarea>
            <button type="submit">Lagre notat</button>
          </form>
        </div>
        <div class="notes-list">
          <h2>Mine notater</h2>
          <div id="notes-container"></div>
        </div>
      `;
      appContainer.appendChild(newNoteManagement);

      // Kobler til event listener for det nye skjemaet
      attachNoteFormListener();
    }

    hentNotater();

    // Setter opp automatisk oppdatering for vanlige brukere
    if (!window.noteRefreshInterval) {
      window.noteRefreshInterval = setInterval(async () => {
        if (!currentUser.er_admin) {
          // Oppdaterer kun for vanlige brukere
          await hentNotater();
        }
      }, 30000); // 30 sekunder
    }
  }
}

// Funksjon for å rydde opp notat-relaterte elementer fra DOM
function cleanupNoteElements() {
  const noteManagement = document.getElementById("note-management");
  const noteForm = document.getElementById("note-form");
  const notesList = document.querySelector(".notes-list");
  const notesContainer = document.getElementById("notes-container");
  const noteFormDiv = document.querySelector(".note-form");

  // Fjerner elementer fra DOM
  if (noteManagement) noteManagement.remove();
  if (noteForm) noteForm.remove();
  if (notesList) notesList.remove();
  if (notesContainer) notesContainer.remove();
  if (noteFormDiv) noteFormDiv.remove();

  // Fjerner også h2-elementer som kan inneholde "Mine notater"
  const allH2 = document.querySelectorAll("h2");
  allH2.forEach((h2) => {
    if (
      h2.textContent.includes("Mine notater") ||
      h2.textContent.includes("Nytt notat")
    ) {
      h2.remove();
    }
  });
}

// Håndtering av brukerutlogging
// Nullstiller autentiseringsdata og går tilbake til innloggingsskjerm
logoutBtn.addEventListener("click", () => {
  accessToken = null;
  currentUser = null;
  document.body.classList.remove("admin-user"); // Fjerner admin-klasse ved utlogging
  cleanupNoteElements(); // Rydder opp notatelementer før app-container skjules

  // Fjerner eksisterende oppdateringsintervaller
  if (window.noteRefreshInterval) {
    clearInterval(window.noteRefreshInterval);
    window.noteRefreshInterval = null;
  }

  appContainer.style.display = "none";
  authContainer.style.display = "block";
});

// Henter alle notater for innlogget bruker
// Sender GET-forespørsel til /notes endepunktet
async function hentNotater() {
  const response = await fetch(`${apiBaseUrl}/notes/`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (response.ok) {
    const notater = await response.json();
    visNotater(notater);
  } else {
    alert("Kunne ikke hente notater");
  }
}

// Viser notatene i brukergrensesnittet
// Oppretter HTML-elementer for hvert notat med rediger- og slett-funksjonalitet
function visNotater(notater) {
  notesContainer.innerHTML = "";
  notater.forEach((notat) => {
    const div = document.createElement("div");
    div.className = "note";
    div.innerHTML = `
            <h3>${notat.tittel}</h3>
            <p>${notat.innhold}</p>
            <button onclick="slettNotat(${notat.id})">Slett</button>
            <button onclick="redigerNotat(${notat.id}, '${notat.tittel}', '${notat.innhold}')">Rediger</button>
        `;
    notesContainer.appendChild(div);
  });
}

// Funksjon for å koble til notatskjema event listener
function attachNoteFormListener() {
  const currentNoteForm = document.getElementById("note-form");
  if (currentNoteForm) {
    currentNoteForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const tittel = document.getElementById("note-title").value;
      const innhold = document.getElementById("note-content").value;

      const response = await fetch(`${apiBaseUrl}/notes/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ tittel, innhold }),
      });

      if (response.ok) {
        currentNoteForm.reset();
        // Henter og viser oppdaterte notater umiddelbart
        await hentNotater();
      } else {
        alert("Kunne ikke lagre notat");
      }
    });
  }
}

// Initiell tilkobling av notatskjema listener
if (noteForm) {
  attachNoteFormListener();
}

// Håndtering av sletting av notater
// Sender DELETE-forespørsel til /notes/{id} endepunktet
async function slettNotat(id) {
  if (!confirm("Er du sikker på at du vil slette dette notatet?")) return;

  const response = await fetch(`${apiBaseUrl}/notes/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (response.ok) {
    hentNotater();
  } else {
    alert("Kunne ikke slette notat");
  }
}

// Håndtering av notatredigering
// Bruker prompt-dialoger for å få nye verdier fra brukeren
function redigerNotat(id, gammelTittel, gammeltInnhold) {
  const nyTittel = prompt("Ny tittel:", gammelTittel);
  if (nyTittel === null) return;
  const nyttInnhold = prompt("Nytt innhold:", gammeltInnhold);
  if (nyttInnhold === null) return;

  oppdaterNotat(id, nyTittel, nyttInnhold);
}

// Sender oppdaterte notatdata til serveren
// Sender PUT-forespørsel til /notes/{id} endepunktet
async function oppdaterNotat(id, tittel, innhold) {
  const response = await fetch(`${apiBaseUrl}/notes/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ tittel, innhold }),
  });

  if (response.ok) {
    hentNotater();
  } else {
    alert("Kunne ikke oppdatere notat");
  }
}

// Henter liste over alle brukere (kun for admin)
// Sender GET-forespørsel til /admin/brukere endepunktet
async function hentBrukere() {
  const response = await fetch(`${apiBaseUrl}/admin/brukere`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (response.ok) {
    const brukere = await response.json();
    visBrukere(brukere);
  } else {
    alert("Kunne ikke hente brukere");
  }
}

// Viser brukerlisten i admin-panelet
// Inkluderer brukerinformasjon og deres notater
function visBrukere(brukere) {
  userList.innerHTML = "";
  brukere.forEach((bruker) => {
    const div = document.createElement("div");
    div.className = "user";

    // Oppretter brukerhode med slett- og passordendring-knapper
    div.innerHTML = `
      <h3>${bruker.brukernavn} ${bruker.er_admin ? "(Admin)" : ""}</h3>
      <div class="user-actions">
        <button onclick="slettBruker(${bruker.id})">Slett bruker</button>
        <button onclick="visAdminPassordEndring(${bruker.id}, '${
      bruker.brukernavn
    }')" class="change-password-btn">Endre passord</button>
      </div>
    `;

    // Legger til brukerens notater hvis de eksisterer
    if (bruker.notater && bruker.notater.length > 0) {
      const notesDiv = document.createElement("div");
      notesDiv.className = "user-notes";
      notesDiv.innerHTML = `
        <h4>Brukerens notater:</h4>
        <div class="notes-list">
          ${bruker.notater
            .map(
              (notat) => `
            <div class="note">
              <h5>${notat.tittel}</h5>
              <p>${notat.innhold}</p>
            </div>
          `
            )
            .join("")}
        </div>
      `;
      div.appendChild(notesDiv);
    } else {
      const noNotesDiv = document.createElement("div");
      noNotesDiv.className = "user-notes";
      noNotesDiv.innerHTML = "<p>Ingen notater</p>";
      div.appendChild(noNotesDiv);
    }

    userList.appendChild(div);
  });
}

// Håndtering av brukersletting (kun for admin)
// Sender DELETE-forespørsel til /admin/brukere/{id} endepunktet
async function slettBruker(id) {
  if (
    !confirm(
      "Er du sikker på at du vil slette denne brukeren og alle dens notater?"
    )
  )
    return;

  const response = await fetch(`${apiBaseUrl}/admin/brukere/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (response.ok) {
    hentBrukere();
  } else {
    alert("Kunne ikke slette bruker");
  }
}

// Funksjonalitet for endring av passord
const changePasswordBtn = document.getElementById("change-password-btn");
const passwordModal = document.getElementById("password-modal");
const adminPasswordModal = document.getElementById("admin-password-modal");
const changePasswordForm = document.getElementById("change-password-form");
const adminChangePasswordForm = document.getElementById(
  "admin-change-password-form"
);
let currentUserToChangePassword = null;

// Lukker modaler når man klikker utenfor
window.onclick = function (event) {
  if (event.target === passwordModal) {
    passwordModal.style.display = "none";
  }
  if (event.target === adminPasswordModal) {
    adminPasswordModal.style.display = "none";
  }
};

// Lukkeknapper for modaler
document.querySelectorAll(".close").forEach((closeBtn) => {
  closeBtn.onclick = function () {
    passwordModal.style.display = "none";
    adminPasswordModal.style.display = "none";
  };
});

// Viser passordendring-modal for vanlige brukere
changePasswordBtn.onclick = function () {
  passwordModal.style.display = "block";
};

// Viser passordendring-modal for admin som endrer brukerpassord
function visAdminPassordEndring(brukerId, brukernavn) {
  currentUserToChangePassword = brukerId;
  document.getElementById(
    "admin-password-username"
  ).textContent = `Endre passord for: ${brukernavn}`;
  adminPasswordModal.style.display = "block";
}

// Håndterer passordendring for vanlige brukere
changePasswordForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const gammeltPassord = document.getElementById("old-password").value;
  const nyttPassord = document.getElementById("new-password").value;

  const response = await fetch(`${apiBaseUrl}/auth/change-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      gammelt_passord: gammeltPassord,
      nytt_passord: nyttPassord,
    }),
  });

  if (response.ok) {
    alert("Passord endret");
    passwordModal.style.display = "none";
    changePasswordForm.reset();
  } else {
    const data = await response.json();
    alert("Feil: " + data.msg);
  }
});

// Håndterer admin passordendring for brukere
adminChangePasswordForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const nyttPassord = document.getElementById("admin-new-password").value;

  const response = await fetch(
    `${apiBaseUrl}/admin/brukere/${currentUserToChangePassword}/change-password`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ nytt_passord: nyttPassord }),
    }
  );

  if (response.ok) {
    alert("Passord endret");
    adminPasswordModal.style.display = "none";
    adminChangePasswordForm.reset();
    currentUserToChangePassword = null;
  } else {
    const data = await response.json();
    alert("Feil: " + data.msg);
  }
});
