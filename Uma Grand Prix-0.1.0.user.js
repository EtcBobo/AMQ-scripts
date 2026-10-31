// ==UserScript==
// @name         Uma Grand Prix
// @namespace    https://github.com/klouie1092
// @version      0.1.0
// @description  Uma Grand Prix game mode for AMQ (2v2, 3v3 or 4v4, speed mode)
// @match        https://*.animemusicquiz.com/*
// @grant        none
// @require      https://github.com/joske2865/AMQ-Scripts/raw/master/common/amqScriptInfo.js
// @icon         https://www.google.com/s2/favicons?sz=64&domain=animemusicquiz.com
// ==/UserScript==

"use strict";

(function () {
    // Victory points by placement (1st to 8th).
    const VICTORY_POINTS = [10, 8, 7, 6, 5, 4, 3, 2];
    const VALID_PLAYER_COUNTS = [4, 6, 8]; // 2v2, 3v3, 4v4
    const COMMAND_PREFIX = "/";
    const MAX_CHAT_LENGTH = 140;
    const MESSAGE_DELAY_MS = 400;
    const DEBUG = true; // logs scores to the browser console after every song

    let umaInProgress = false;
    let umaState = null;

    if (typeof Listener === "undefined") return;

    // Wait for AMQ to finish loading.
    const loadInterval = setInterval(() => {
        if (document.querySelector("#loadingScreen.hidden")) {
            clearInterval(loadInterval);
            setup();
        }
    }, 500);

    function setup() {
        new Listener("game chat update", (data) => {
            if (!data || !Array.isArray(data.messages)) return;

            for (const message of data.messages) {
                if (!message || message.sender !== selfName) continue;

                if (
                    typeof message.message !== "string" ||
                    !/^\/uma(?:\s|$)/i.test(message.message.trim())
                ) {
                    continue;
                }

                parseCommand(message.message);
            }
        }).bindListener();

        new Listener("answer results", (result) => {
            if (umaInProgress) {
                processAnswerResults(result);
            }
        }).bindListener();

        console.log("[Uma Grand Prix] Listeners registered.");
    }

    // ---------- Chat helpers ----------

    const chatQueue = [];
    let chatTimer = null;

    function sendChatMessage(msg) {
        chatQueue.push(msg);
        if (!chatTimer) drainChatQueue();
    }

    function drainChatQueue() {
        const msg = chatQueue.shift();

        if (msg === undefined) {
            chatTimer = null;
            return;
        }

        rawSend(msg);
        chatTimer = setTimeout(drainChatQueue, MESSAGE_DELAY_MS);
    }

    function rawSend(msg) {
        if (!socket?.sendCommand) {
            console.warn("[Uma Grand Prix] AMQ socket is unavailable.");
            return;
        }

        socket.sendCommand({
            type: "lobby",
            command: "game chat message",
            data: {
                msg,
                teamMessage: false
            }
        });
    }

    // Sends "prefix item | item | item", splitting into several messages if too long.
    function sendChunked(prefix, items) {
        let line = prefix;
        let hasItem = false;

        for (const item of items) {
            const candidate = hasItem ? `${line} | ${item}` : `${line}${item}`;

            if (candidate.length > MAX_CHAT_LENGTH && hasItem) {
                sendChatMessage(line);
                line = `${prefix}${item}`;
            } else {
                line = candidate;
                hasItem = true;
            }
        }

        if (hasItem) sendChatMessage(line);
    }

    function ordinal(n) {
        const suffixes = ["th", "st", "nd", "rd"];
        const v = n % 100;
        return n + (suffixes[(v - 20) % 10] || suffixes[v] || suffixes[0]);
    }

    // ---------- Commands ----------

    function parseCommand(input) {
        const parts = input.trim().split(/\s+/);
        const command = parts[0].slice(COMMAND_PREFIX.length).toLowerCase();
        const args = parts.slice(1);

        if (command !== "uma") return;

        if (args[0]?.toLowerCase() === "stop") {
            if (umaInProgress) {
                stopUmaGame("Uma Grand Prix stopped.");
            } else {
                sendChatMessage("No Uma Grand Prix is currently running.");
            }
            return;
        }

        if (args.length !== 1) {
            sendChatMessage("Usage: /uma [points to win the round] or /uma stop");
            return;
        }

        const threshold = Number(args[0]);

        if (!Number.isInteger(threshold) || threshold <= 0) {
            sendChatMessage("Please enter a positive whole number of points.");
            return;
        }

        if (umaInProgress) {
            sendChatMessage("Uma Grand Prix is already in progress.");
            return;
        }

        if (typeof quiz === "undefined" || !quiz?.players) {
            sendChatMessage("Unable to read the current lobby players.");
            return;
        }

        const players = getOrderedPlayers();

        if (!VALID_PLAYER_COUNTS.includes(players.length)) {
            sendChatMessage(
                "Uma Grand Prix requires 4, 6 or 8 players (2v2, 3v3 or 4v4)."
            );
            return;
        }

        const teamNumbers = players.map(player => player.teamNumber);

        if (
            teamNumbers.some(number => number === undefined || number === null) ||
            new Set(teamNumbers).size !== players.length
        ) {
            sendChatMessage(
                "Unable to determine the player order. Please check the lobby."
            );
            return;
        }

        umaState = {
            threshold,
            playerCount: players.length,
            songsPlayed: 0
        };

        umaInProgress = true;

        const teamSize = players.length / 2;

        sendChatMessage(
            `Uma Grand Prix started! ${teamSize}v${teamSize}. First to ${threshold} points ends the round!`
        );
    }

    // Left team = first half by teamNumber, right team = second half.
    function getOrderedPlayers() {
        if (typeof quiz === "undefined" || !quiz?.players) return [];

        return Object.values(quiz.players).sort(
            (a, b) => Number(a.teamNumber) - Number(b.teamNumber)
        );
    }

    // ---------- Game logic ----------

    function processAnswerResults(result) {
        if (!umaInProgress || !umaState) return;

        const players = getOrderedPlayers();

        if (players.length !== umaState.playerCount) {
            stopUmaGame("Player count changed. Uma Grand Prix stopped.");
            return;
        }

        umaState.songsPlayed += 1;

        // Read the in-game (speed mode) score for each player.
        const scoreById = new Map();

        for (const playerResult of result.players || []) {
            const score = Number(playerResult.score);
            scoreById.set(
                playerResult.gamePlayerId,
                Number.isFinite(score) ? score : 0
            );
        }

        const half = players.length / 2;

        const entries = players.map((player, index) => ({
            name: player.name,
            team: index < half ? "Left" : "Right",
            score: scoreById.get(player.gamePlayerId) ?? 0
        }));

        if (DEBUG) {
            console.log(
                `[Uma Grand Prix] Song ${umaState.songsPlayed} scores:`,
                entries.map(e => `${e.team} ${e.name}: ${e.score}`),
                "raw result:",
                result
            );
        }

        const reached = entries.filter(e => e.score >= umaState.threshold);

        if (reached.length === 0) {
            // Round continues: show each team's current victory points.
            const { totals } = rankEntries(entries);

            sendChatMessage(
                `Current victory points: Left ${totals.Left} - ${totals.Right} Right`
            );
            return;
        }

        endRound(entries, reached);
    }

    // Ranks by in-game score. Ties share the same placement and victory points.
    function rankEntries(entries) {
        const sorted = [...entries].sort((a, b) => b.score - a.score);

        sorted.forEach((entry, index) => {
            entry.rank =
                index > 0 && entry.score === sorted[index - 1].score
                    ? sorted[index - 1].rank
                    : index + 1;
            entry.victoryPoints = VICTORY_POINTS[entry.rank - 1] ?? 0;
        });

        const totals = { Left: 0, Right: 0 };
        for (const entry of sorted) {
            totals[entry.team] += entry.victoryPoints;
        }

        return { sorted, totals };
    }

    function endRound(entries, reached) {
        const threshold = umaState.threshold;

        sendChunked(
            "Uma Grand Prix: ",
            reached.map(e => e.name)
        );
        sendChatMessage(
            `reached ${threshold} points! The round is over. Calculating victory points...`
        );

        const { sorted, totals } = rankEntries(entries);

        // One message per player, in placement order.
        for (const entry of sorted) {
            sendChatMessage(
                `${ordinal(entry.rank)} Place: ${entry.name} (${entry.team}) ${entry.score} pts - ${entry.victoryPoints} Victory points`
            );
        }

        sendChatMessage(
            `Final victory points: Left ${totals.Left} - ${totals.Right} Right`
        );

        if (totals.Left > totals.Right) {
            sendChatMessage("Uma Grand Prix completed! Left team wins!");
        } else if (totals.Right > totals.Left) {
            sendChatMessage("Uma Grand Prix completed! Right team wins!");
        } else {
            sendChatMessage("Uma Grand Prix ended in a draw!");
        }

        umaInProgress = false;
        umaState = null;
    }

    function stopUmaGame(message) {
        umaInProgress = false;
        umaState = null;
        sendChatMessage(message);
    }
})();
