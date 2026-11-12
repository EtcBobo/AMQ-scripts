// ==UserScript==
// @name         NGMC Manual Counter C1.0
// @namespace    https://github.com/RomainTho/AMQ-scripts
// @version      1.6
// @description  AMQ NGMC Guess Counter for tour players
// @author       RomainTho
// @match        https://animemusicquiz.com/*
// @require      https://raw.githubusercontent.com/TheJoseph98/AMQ-Scripts/master/common/amqWindows.js
// @require      https://raw.githubusercontent.com/TheJoseph98/AMQ-Scripts/master/common/amqScriptInfo.js
// @grant        none
// ==/UserScript==

if (document.getElementById("startPage")) return;

// Starting value for each of the four player rows (editable per player in the UI)
const DEFAULT_INITIAL = [4, 3, 2, 1];

// Each player has an initial value (only changed from the UI) and a current count (changes during the game)
let players = DEFAULT_INITIAL.map((initial, i) => ({ name: `Player ${i + 1}`, initial, count: initial }));
let managerWindow;

// Whether guess changes are sent to the chat (controlled by the checkbox)
let sendGuess = true;

// Team lives: Reset Lives puts both teams back to this value
const DEFAULT_LIVES = 5;
let leftLife = DEFAULT_LIVES;
let rightLife = DEFAULT_LIVES;


// Send a chat message
function sendChatMessage(message, isTeamMessage) {
    socket.sendCommand({
        type: "lobby",
        command: "game chat message",
        data: {
            msg: String(message),
            teamMessage: Boolean(isTeamMessage)
        }
    });
}

// Automatically send the guess message (if the checkbox is ticked)
function updateMessage() {
    if (!sendGuess) return;
    sendChatMessage(players.map(p => p.count).join(""), false);
}

// Lives are always sent to the chat
function updateLifeDisplay() {
    $("#leftLife").text(leftLife);
    $("#rightLife").text(rightLife);
    sendChatMessage(`${leftLife}-${rightLife}`, false);
}

// Main function that builds the window
function createNGMCManagerWindow() {
    managerWindow = new AMQWindow({
        id: "ngmcWindow",
        title: "Guess Counter",
        width: 300,
        height: 240,
        zIndex: 1054,
        draggable: true
    });

    // Panels
    managerWindow.addPanel({ width: 1.0, height: 130, position: { x: 0, y: 0 }, id: "counterPanel" });
    managerWindow.addPanel({ width: 1.0, height: 30, position: { x: 0, y: 132 }, id: "customPanel" });
    managerWindow.addPanel({ width: 1.0, height: 70, position: { x: 0, y: 166 }, id: "lifePanel" });

    // Reset buttons
    $("#customPanel").append(`
        <button id="resetGuesses" class="btn btn-danger" style="width: 48%;">Reset Guesses</button>
        <button id="resetLives" style="
            width: 48%;
            padding: 4px 8px;
            background-color: #7f8c8d;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
        ">
            Reset Lives
        </button>
    `);

    // Lives area
    $("#lifePanel").append(`
        <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 5px;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <button id="leftLifeMinus" class="btn btn-danger">-</button>
                <span id="leftLife" style="min-width: 20px; text-align: center;">${leftLife}</span>
                <button id="leftLifePlus" class="btn btn-success">+</button>
            </div>

            <div style="display: flex; flex-direction: column; align-items: center; font-weight: bold;">
                <span> - </span>
                <div style="display: flex; gap: 40px; font-weight: normal; font-size: 12px;">
                    <span>Team 1</span>
                    <span>Team 2</span>
                </div>
            </div>

            <div style="display: flex; align-items: center; gap: 5px;">
                <button id="rightLifeMinus" class="btn btn-danger">-</button>
                <span id="rightLife" style="min-width: 20px; text-align: center;">${rightLife}</span>
                <button id="rightLifePlus" class="btn btn-success">+</button>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; align-items: start; padding-left: 5px;">
            <label><input type="checkbox" id="chatEnabledGuesses" checked> Activate chat guesses</label>
        </div>
    `);

    $("#chatEnabledGuesses").on("change", function () {
        sendGuess = $(this).prop("checked");
    });

    displayCounters();

    // Life buttons (no upper cap, minimum 0)
    $("#leftLifeMinus").click(() => {
        if (leftLife > 0) leftLife--;
        updateLifeDisplay();
    });

    $("#leftLifePlus").click(() => {
        leftLife++;
        updateLifeDisplay();
    });

    $("#rightLifeMinus").click(() => {
        if (rightLife > 0) rightLife--;
        updateLifeDisplay();
    });

    $("#rightLifePlus").click(() => {
        rightLife++;
        updateLifeDisplay();
    });

    // Reset guesses: each player goes back to their own initial value
    $("#resetGuesses").click(() => {
        players.forEach(p => {
            p.count = p.initial;
        });
        updateMessage();
        displayCounters();
    });

    // Reset the team lives
    $("#resetLives").click(() => {
        leftLife = DEFAULT_LIVES;
        rightLife = DEFAULT_LIVES;
        updateLifeDisplay();
    });
}

// Display the counters
function displayCounters() {
    $("#counterPanel").empty();
    $("#counterPanel").append(`
        <div style="display: flex; align-items: center; margin: 0 10px; font-size: 11px; opacity: 0.7;">
            <span style="flex: 1;">Player</span>
            <span style="width: 44px; margin-right: 8px; text-align: center;">Start</span>
            <span style="width: 82px; text-align: center;">Current</span>
        </div>
    `);
    players.forEach((p, i) => {
        const row = createPlayerRow(p, i);
        $("#counterPanel").append(row);
    });
}

function createPlayerRow(p, i) {
    return $(`
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 2px 10px;">
            <span style="flex: 1; font-weight: bold;">${p.name}</span>
            <input id="initial${i}" class="playerInitial" type="number" min="0" step="1" value="${p.initial}" title="Starting value for ${p.name}">
            <button class="btn btn-danger" id="minus${i}" style="width: 26px;">-</button>
            <span id="count${i}" style="width: 30px; text-align: center;">${p.count}</span>
            <button class="btn btn-success" id="plus${i}" style="width: 26px;">+</button>
        </div>
    `).on("keydown", `#initial${i}`, event => {
        // Stop AMQ keyboard shortcuts from firing while typing
        event.stopPropagation();
    }).on("change", `#initial${i}`, function () {
        // Player's initial value changed: their current count follows it (no chat message is sent)
        const value = parseInt($(this).val(), 10);
        if (isNaN(value) || value < 0) {
            $(this).val(p.initial);
            return;
        }
        p.initial = value;
        p.count = value;
        $(`#count${i}`).text(p.count);
    }).on("click", `#plus${i}`, () => {
        p.count++;
        $(`#count${i}`).text(p.count);
        updateMessage();
    }).on("click", `#minus${i}`, () => {
        if (p.count > 0) p.count--;
        $(`#count${i}`).text(p.count);
        updateMessage();
    });
}


// send a client side message to game chat
function sendSystemMessage(message, message2) {
    if (gameChat.open) {
        if (message2) {
            setTimeout(() => { gameChat.systemMessage(String(message), String(message2)) }, 1);
        }
        else {
            setTimeout(() => { gameChat.systemMessage(String(message)) }, 1);
        }
    }
    else if (nexus.inCoopLobby) {
        setTimeout(() => { nexusCoopChat.displayServerMessage({message: String(message)}) }, 1);
    }
}

let loadInterval = setInterval(() => {
    if ($("#loadingScreen").hasClass("hidden")) {
        createNGMCManagerWindow();
        clearInterval(loadInterval);
    }
}, 500);

// Add the button to the top-right bar
let oldWidth = $("#qpOptionContainer").width();
$("#qpOptionContainer").width(oldWidth + 35);

$("#qpOptionContainer > div").append($(`<div id="ngmcqpasScript" class="clickAble qpOption"><i aria-hidden="true" class="fa fa-calculator qpMenuItem"></i></div>`)
  .click(() => {
    if (managerWindow.isVisible()) {
      managerWindow.close();
    } else {
      managerWindow.open(() => { });
    }
  })
  .popover({
    content: "NGMC Counting",
    trigger: "hover",
    placement: "bottom"
  })
);

AMQ_addStyle(`
    #ngmcWindow .customWindowBody {
        height: 235px !important;
    }
`);

AMQ_addStyle(`
    #ngmcWindow {
        background-color: #2e2e2e;
        color: #fff;
    }
    #ngmcqpasScript {
        width: 27px;
        margin-right: 5px;
    }
`);
AMQ_addStyle(`
    #ngmcWindow .modal-header {
        padding: 8px;
    }

    #ngmcWindow .modal-title {
        font-size: 14px;
    }
`);
AMQ_addStyle(`
    /* Smaller buttons */
    #ngmcWindow .customWindowPanel button {
        height: 22px !important;
        padding: 1px 4px !important;
        font-size: 12px !important;
    }

    /* Initial value inputs */
    #ngmcWindow .playerInitial {
        width: 60px;
        height: 22px !important;
        padding: 2px 4px !important;
        font-size: 12px !important;
        background-color: white;
        color: black;
        border: 1px solid #ccc;
        border-radius: 4px;
        box-sizing: border-box;
    }
    #ngmcWindow .playerInitial {
        width: 44px;
        margin-right: 8px;
    }

    /* Smaller header padding */
    #ngmcWindow .customWindowHeader {
        padding: 4px 8px !important;
        height: 28px !important;
    }

    #ngmcWindow .customWindowHeader .modal-title {
        font-size: 14px !important;
        margin: 0 !important;
    }
`);

AMQ_addStyle(`
    #ngmcWindow button {
        height: 24px !important;
        font-size: 11px !important;
        padding: 2px 4px !important;
    }
    #ngmcWindow .customWindowBody {
        overflow: hidden !important;
    }
`);
