'use strict';

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const esc = (text) => String(text).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const API = {
  async get(path) {
    const response = await fetch(path);
    return response.json();
  },
  async post(path, body = {}) {
    const response = await fetch(path, {
      method: 'POST',
      headers: { 'X-Game': '1', 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return response.json();
  },
};

const FIGHTER_COLORS = {
  'Yuji Itadori': '#fb923c', 'Satoru Gojo': '#38bdf8', 'Choso Kamo': '#dc2626', 'Maki Zenin': '#22c55e',
  'Megumi Fushiguro': '#3b82f6', 'Aoi Todo': '#d97706', 'Yuki Tsukumo': '#eab308', 'Yuta Okkotsu': '#cbd5e1',
  'Kento Nanami': '#ca8a04', 'Ryomen Sukuna': '#ef4444', 'Toji Fushiguro': '#64748b', 'Kenjaku': '#8b5cf6',
  'Mahito': '#818cf8', 'Jogo': '#f97316', 'Uraume': '#67e8f9', 'Naoya Zenin': '#f59e0b',
  'Kinji Hakari': '#ec4899', 'Toge Inumaki': '#10b981', 'Hiromi Higuruma': '#94a3b8',
  'Hajime Kashimo': '#facc15', 'Mei Mei': '#a78bfa',
};

function colorOf(name) {
  if (FIGHTER_COLORS[name]) return FIGHTER_COLORS[name];
  let hash = 0;
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) % 360;
  return `hsl(${hash}, 70%, 60%)`;
}

function initials(name) {
  const words = name.split(' ').filter(Boolean);
  if (words.length === 1) return words[0].slice(0, 2);
  return (words[0][0] + words[words.length - 1][0]).toUpperCase();
}

function avatar(name, size = '') {
  return `<div class="avatar ${size}" style="--c:${colorOf(name)}"><span>${esc(initials(name))}</span></div>`;
}

function moveKind(label) {
  if (label.startsWith('Damage')) return 'dmg';
  if (label.startsWith('Heal')) return 'heal';
  if (label.startsWith('Domain')) return 'dom';
  return 'util';
}


const PAGE_ID = Math.random().toString(36).slice(2);   // lets the server tell a reload from a close
let boot = null;                       // data from the server: roster, modes, settings
let current = 'title';
const setup = { mode: 1, names: ['Player 1', 'Player 2'], picks: [null, null], slot: 0, preview: 0 };
let battle = null;                     // the match being watched, or null

function show(name) {
  current = name;
  $$('.screen').forEach((el) => el.classList.toggle('active', el.id === `screen-${name}`));
  if (name === 'howto') renderHowTo(howtoTab);
  if (name === 'modes') renderModes();
  if (name === 'select') renderSelect();
  if (name === 'stats') renderStats();
  if (name === 'settings') renderSettings();
}

function modalOpen() { return !$('#modal-root').classList.contains('hidden'); }

function openModal(html, buttons = [], { cls = '', dismiss = true, stack = false } = {}) {
  const root = $('#modal-root');
  root.innerHTML = `<div class="modal ${cls}">${html}<div class="btns"></div></div>`;
  const holder = $('.btns', root);
  if (stack) holder.classList.add('stack');
  buttons.forEach((b) => {
    const el = document.createElement('button');
    el.className = `btn ${b.cls || ''}`;
    el.textContent = b.label;
    el.onclick = () => { if (b.close !== false) closeModal(); if (b.onClick) b.onClick(); };
    holder.appendChild(el);
  });
  root.onclick = dismiss ? (e) => { if (e.target === root) closeModal(); } : null;
  root.classList.remove('hidden');
  const first = $('.btns .btn', root);
  if (first) first.focus();
}

function closeModal() {
  const root = $('#modal-root');
  root.classList.add('hidden');
  root.innerHTML = '';
}

let toastTimer = null;
function toast(message) {
  const el = $('#toast');
  el.textContent = message;
  el.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add('hidden'), 3500);
}


let howtoTab = 'basics';

function howtoPages() {
  const turns = boot.max_turns;
  return [
    { id: 'basics', title: 'The basics', html: `
      <h3>The goal</h3>
      <p>Bring your opponent's <b>HP</b> to 0 before they do the same to you. If nobody has won after <b>${turns} turns</b>, the match is a draw.</p>
      <div class="howto-grid">
        <div class="howto-card"><b>1. Take turns</b><p>Every turn both fighters act once: Player 1 first, then Player 2. On your turn, pick <b>one move</b>.</p></div>
        <div class="howto-card"><b>2. Read the moves</b><p>Each move button shows its damage or healing, its CE cost and its cooldown. The small text explains what it does.</p></div>
        <div class="howto-card"><b>3. Watch the log</b><p>Everything that happens appears in the battle log. Press <b>Space</b> or <b>Skip text</b> to speed it up.</p></div>
        <div class="howto-card"><b>4. Know your opponent</b><p>Press <b>Inspect opponent</b> during your turn to see all of their moves and passives.</p></div>
      </div>
      <ul><li>Some moves can't be dodged, and a few (Mahoraga, Black Hole) destroy the battlefield and end the match in a draw.</li>
      <li>If you are <span class="chip cyan">Frozen</span> you lose your next turn.</li></ul>` },
    { id: 'energy', title: 'Energy & cooldowns', html: `
      <h3>Cursed energy (CE)</h3>
      <p>The blue bar is your <b>cursed energy</b>. Most moves cost CE. If you can't afford a move, its button is greyed out.</p>
      <div class="howto-grid">
        <div class="howto-card"><b>Focus</b><p>Skip your attack to regain <b>20-35 CE</b>. It costs nothing and has no cooldown.</p></div>
        <div class="howto-card"><b>Passive regeneration</b><p>At the end of your turn you also regain <b>2-8 CE</b> on your own.</p></div>
        <div class="howto-card"><b>No cursed energy</b><p>Maki and Toji have no CE at all. Their moves are free, but they have less HP and domains hit them harder.</p></div>
      </div>
      <h3 style="margin-top:22px">Cooldowns</h3>
      <p>After you use a move it can't be used again for a number of your turns (its <b>CD</b>). Strong moves have long cooldowns, and many start the match already on cooldown. A greyed button tells you how many turns remain.</p>` },
    { id: 'combat', title: 'Combat', html: `
      <h3>How hits work</h3>
      <ul>
        <li><b>Damage varies</b> a little every hit, and about 1 in 10 hits is a <b>critical hit</b> for extra damage.</li>
        <li><b>Dodging:</b> most fighters dodge about 7% of attacks. Gojo and Maki dodge about 17%, Toji about 21%. Todo's Boogie Woogie can raise his chance to about 41% until it triggers, and Naoya gets harder to hit as his Speed stacks grow.</li>
        <li><b>Healing</b> moves restore HP up to your maximum.</li>
        <li><b>Mahito</b> takes about 11% less damage from most attacks. Moves that say <i>"Bypasses Mahito's soul resistance"</i> ignore that.</li>
      </ul>
      <p style="margin-top:14px">Every fighter also has a passive or special mechanic. Read it under <b>Passive / Tip</b> on the fighter's card.</p>` },
    { id: 'domains', title: 'Domains', html: `
      <h3>Domain expansion</h3>
      <p>Most fighters have a <b>domain</b>: a powerful move that costs about 50 CE and starts the match on a long cooldown. Opening it uses your turn, then it lasts <b>4 turns</b> and gives your attacks a special bonus. Each domain is different, so read its description.</p>
      <div class="howto-grid">
        <div class="howto-card"><b>Attacking domains</b><p>Boost your damage (Malevolent Shrine, Coffin of the Iron Mountain, Womb Profusion and more), sometimes with healing or extra effects.</p></div>
        <div class="howto-card"><b>Defensive domains</b><p>Unlimited Void halves the damage you take. Chimera Shadow Garden cuts it to a third while adding shadow-clone damage.</p></div>
        <div class="howto-card"><b>Simple Domain</b><p>Many fighters can use it to shield themselves against the next <b>2 enemy turns</b>: attacks deal 35% less damage, or 50% less against a fighter whose domain is open.</p></div>
      </div>` },
    { id: 'status', title: 'Status effects', html: `
      <h3>What the tags mean</h3>
      <p>Colored tags under a fighter's bars show what is affecting them.</p>
      <div class="howto-grid">
        <div class="howto-card"><span class="chip red">Burning</span><p>Takes 8 damage at the start of its turn, for 2 turns.</p></div>
        <div class="howto-card"><span class="chip cyan">Frozen</span><p>Loses its next turn.</p></div>
        <div class="howto-card"><span class="chip cyan">Chill x2</span><p>From Uraume. Each stack makes that fighter deal 4% less damage (up to 4 stacks).</p></div>
        <div class="howto-card"><span class="chip red">Blood x3</span><p>Choso's stacks on the enemy. Supernova explodes them for extra damage.</p></div>
        <div class="howto-card"><span class="chip yellow">Speed x2</span><p>Naoya's stacks. Each adds damage to all his attacks and improves his dodging.</p></div>
        <div class="howto-card"><span class="chip yellow">Overtime</span><p>Nanami below half HP: more damage dealt and 10% less damage taken.</p></div>
        <div class="howto-card"><span class="chip magenta">Domain</span><p>This fighter's domain is open. The number is the turns left.</p></div>
        <div class="howto-card"><span class="chip blue">Simple Domain</span><p>This fighter is shielded against incoming attacks.</p></div>
        <div class="howto-card"><span class="chip white">Crows / Charge / Strain</span><p>Special resources for Mei Mei, Kashimo and Inumaki. See their fighter cards.</p></div>
      </div>` },
    { id: 'tips', title: 'Tips', html: `
      <h3>Tips for your first matches</h3>
      <ul>
        <li><b>Don't burn all your CE early.</b> Keep enough for your big move, and use <b>Focus</b> when you're safe.</li>
        <li><b>Heal when a kill isn't close.</b> Healing moves have cooldowns, so use them before you are in danger.</li>
        <li><b>Plan around cooldowns.</b> Start with moves that are ready while the strong ones recharge.</li>
        <li><b>Save your domain</b> for when you can follow it with strong attacks.</li>
        <li><b>Inspect your opponent</b> to find out whether they can dodge, heal, freeze or end the match.</li>
        <li>New? Try <b>AI vs AI</b> to watch fighters in action, then play <b>Human vs AI</b> on Easy.</li>
      </ul>` },
  ];
}

function renderHowTo(tab) {
  howtoTab = tab;
  const pages = howtoPages();
  const page = pages.find((p) => p.id === tab) || pages[0];
  $('#screen-howto').innerHTML = `
    <div class="head"><button class="btn small" data-back>&larr; Back</button><h2>How to play</h2></div>
    <div class="tabs">${pages.map((p) => `<button class="tab ${p.id === page.id ? 'on' : ''}" data-tab="${p.id}">${esc(p.title)}</button>`).join('')}</div>
    <div class="howto-body">${page.html}</div>`;
  $('[data-back]', $('#screen-howto')).onclick = () => show('title');
  $$('[data-tab]', $('#screen-howto')).forEach((el) => { el.onclick = () => renderHowTo(el.dataset.tab); });
}


const MODE_TEXT = {
  1: ['⚔️', 'You take on the computer. Pick the difficulty in Settings.'],
  2: ['🤝', 'Two players share the keyboard and take turns.'],
  3: ['🤖', 'Pick two fighters and watch them battle it out.'],
};

function modeHumans() { return boot.modes.find((m) => m.id === setup.mode).humans; }

function renderModes() {
  const humans = modeHumans();
  const root = $('#screen-modes');
  root.innerHTML = `
    <div class="head"><button class="btn small" data-back>&larr; Back</button><h2>Choose a game mode</h2></div>
    <div class="mode-row">${boot.modes.map((m) => `
      <button class="mode-card ${m.id === setup.mode ? 'on' : ''}" data-mode="${m.id}">
        <div class="mode-icon">${MODE_TEXT[m.id][0]}</div><h3>${esc(m.label)}</h3><p>${MODE_TEXT[m.id][1]}</p>
      </button>`).join('')}</div>
    <div class="names">${[0, 1].filter((i) => humans[i]).map((i) => `
      <label class="field">Player ${i + 1} name<input data-name="${i}" maxlength="16" value="${esc(setup.names[i])}"></label>`).join('')}</div>
    <div class="foot"><button class="btn primary" id="to-select">Choose fighters &rarr;</button></div>`;
  $('[data-back]', root).onclick = () => show('title');
  $$('[data-mode]', root).forEach((el) => { el.onclick = () => { setup.mode = +el.dataset.mode; renderModes(); }; });
  $$('[data-name]', root).forEach((el) => { el.oninput = () => { setup.names[+el.dataset.name] = el.value; }; });
  $('#to-select', root).onclick = () => {
    setup.picks = [null, null]; setup.slot = 0; setup.preview = 0;
    show('select');
  };
}

function seatLabel(i) {
  if (modeHumans()[i]) return (setup.names[i] || '').trim() || `Player ${i + 1}`;
  return setup.mode === 1 ? 'AI' : `AI ${i + 1}`;
}

function cardHTML(f, live) {
  const hp = live ? `${live.hp}/${live.max_hp}` : f.hp;
  return `
    <div class="card-head">${avatar(f.name, 'lg')}<div><h3>${esc(f.name)}</h3><div class="ttl">${esc(f.title)}</div></div></div>
    <div class="statrow"><span class="lbl">HP</span><div class="mini hp"><i style="width:${Math.min(100, f.hp / 180 * 100)}%"></i></div><span class="val">${hp}</span></div>
    <div class="statrow"><span class="lbl">CE</span>${f.ce > 0
      ? `<div class="mini ce"><i style="width:${Math.min(100, f.ce / 151 * 100)}%"></i></div><span class="val">${f.ce}</span>`
      : '<span>none (Heavenly Restriction)</span>'}</div>
    <div class="tip"><b>Passive / Tip:</b> ${esc(f.tip)}</div>
    ${f.moves.map((m) => `
      <div class="mv"><div class="row"><b>${esc(m.name)}</b><span class="tag-${moveKind(m.label)}">${esc(m.label)}</span>
        <span class="meta">CE ${m.ce} &middot; CD ${m.cd}</span></div>
        ${boot.settings.show_descriptions ? `<div class="d">${esc(m.desc)}</div>` : ''}</div>`).join('')}`;
}

function renderSelect() {
  const root = $('#screen-select');
  const both = setup.picks[0] !== null && setup.picks[1] !== null;
  const slotChip = (i) => {
    const pick = setup.picks[i];
    const f = pick === null ? null : boot.roster[pick];
    return `<button class="slot ${setup.slot === i ? 'cur' : ''} ${f ? '' : 'empty'}" data-slot="${i}">
      ${f ? avatar(f.name, 'sm') : '<div class="avatar sm"><span>?</span></div>'}<span>${esc(seatLabel(i))}${f ? ': ' + esc(f.name) : ''}</span></button>`;
  };
  const heading = both ? 'Ready to fight?' : `${esc(seatLabel(setup.slot))}: choose a fighter`;
  const previewing = boot.roster[setup.preview];
  root.innerHTML = `
    <div class="head"><button class="btn small" data-back>&larr; Back</button><h2>${heading}</h2>
      <div class="slots">${slotChip(0)}<span class="vs">VS</span>${slotChip(1)}</div></div>
    <div class="select-main">
      <div class="grid">${boot.roster.map((f) => {
        const mark = setup.picks.indexOf(f.index);
        return `<button class="tile ${setup.preview === f.index ? 'preview' : ''}" data-i="${f.index}">
          ${mark >= 0 ? `<span class="badge p${mark + 1}">P${mark + 1}</span>` : ''}
          ${avatar(f.name)}<div class="nm">${esc(f.name)}</div><div class="st">HP ${f.hp} &middot; CE ${f.ce}</div></button>`;
      }).join('')}</div>
      <div class="card" id="preview-card">${cardHTML(previewing)}</div>
    </div>
    <div class="foot">
      <button class="btn" id="random">🎲 Random</button>
      ${both
        ? '<button class="btn primary" id="start">⚔️ Start battle</button>'
        : `<button class="btn primary" id="pick">Pick ${esc(previewing.name)}</button>`}
    </div>`;
  $('[data-back]', root).onclick = () => show('modes');
  $$('[data-i]', root).forEach((el) => {
    el.onclick = () => { setup.preview = +el.dataset.i; renderSelect(); };
    el.ondblclick = () => { if (!both) pick(+el.dataset.i); };
  });
  $$('[data-slot]', root).forEach((el) => { el.onclick = () => { setup.slot = +el.dataset.slot; setup.picks[setup.slot] = null; renderSelect(); }; });
  $('#random', root).onclick = () => {
    const free = both ? setup.slot % 2 : setup.slot;
    if (both) { setup.picks[free] = null; setup.slot = free; }
    pick(Math.floor(Math.random() * boot.roster.length));
  };
  const pickBtn = $('#pick', root);
  if (pickBtn) pickBtn.onclick = () => pick(setup.preview);
  const startBtn = $('#start', root);
  if (startBtn) startBtn.onclick = startMatch;
}

function pick(index) {
  setup.picks[setup.slot] = index;
  setup.preview = index;
  setup.slot = setup.picks[0] === null ? 0 : setup.picks[1] === null ? 1 : 2;
  renderSelect();
}


const SPEED_MS = { instant: 0, fast: 130, normal: 380, slow: 760 };

function fighterPanelHTML(i, card, label) {
  return `
    <div class="fighter" data-i="${i}" style="--c:${colorOf(card.name)}">
      ${avatar(card.name)}
      <div class="finfo">
        <div class="who">${esc(label)}</div>
        <div class="fname">${esc(card.name)}<small>${esc(card.title)}</small></div>
        <div class="barrow"><label>HP</label><div class="bar hp"><div class="trail"></div><div class="fill ok"></div></div><span class="num hpnum"></span></div>
        ${card.ce > 0
          ? '<div class="barrow"><label>CE</label><div class="bar ce"><div class="fill"></div></div><span class="num cenum"></span></div>'
          : '<div class="noce">No cursed energy: every move is free</div>'}
        <div class="tags"></div>
      </div>
      <div class="floaters"></div>
    </div>`;
}

function buildBattle(ev) {
  battle.fighters = ev.fighters;
  battle.labels = ev.labels;
  battle.humans = ev.humans;
  const modeLabel = boot.modes.find((m) => m.id === ev.mode).label;
  $('#screen-battle').innerHTML = `
    <div class="topbar">
      <button class="btn small" id="b-menu">☰ Menu</button>
      <span class="turn" id="b-turn">Get ready</span><span class="mode">${esc(modeLabel)}</span><span class="sp"></span>
      <button class="btn small" id="b-skip">⏩ Skip text</button>
    </div>
    <div class="arena">${fighterPanelHTML(0, ev.fighters[0], ev.labels[0])}<div class="vsmark">VS</div>${fighterPanelHTML(1, ev.fighters[1], ev.labels[1])}</div>
    <div class="log" id="log"></div>
    <div class="movepanel" id="movepanel"></div>`;
  $('#b-menu').onclick = confirmLeave;
  $('#b-skip').onclick = () => { battle.skip = true; };
  battle.prev = [null, null];
  applyState(ev.state);
  setWaiting(ev.humans.some(Boolean) ? 'Get ready' : 'Watching the fight');
}

function setWaiting(text) {
  const panel = $('#movepanel');
  if (panel) panel.innerHTML = `<div class="waiting">${esc(text)}<span class="dots"></span></div>`;
}

function floater(panel, delta) {
  const el = document.createElement('span');
  el.className = `floater ${delta < 0 ? 'neg' : 'pos'}`;
  el.textContent = delta < 0 ? String(delta) : `+${delta}`;
  $('.floaters', panel).appendChild(el);
  setTimeout(() => el.remove(), 1200);
}

function flash(panel, cls) {
  panel.classList.remove('hit', 'heal');
  void panel.offsetWidth;                       // restart the animation
  panel.classList.add(cls);
  setTimeout(() => panel.classList.remove(cls), 650);
}

function applyState(states) {
  states.forEach((s, i) => {
    const panel = $(`.fighter[data-i="${i}"]`);
    if (!panel) return;
    const prev = battle.prev[i];
    const percent = Math.max(0, (s.hp / s.max_hp) * 100);
    const fill = $('.hp .fill', panel);
    const trail = $('.hp .trail', panel);
    fill.style.width = `${percent}%`;
    fill.className = `fill ${percent > 50 ? 'ok' : percent > 25 ? 'mid' : 'low'}`;
    if (prev === null || s.hp > prev.hp) {      // the white "damage trail" only follows drops
      trail.style.transition = 'none';
      trail.style.width = `${percent}%`;
      void trail.offsetWidth;
      trail.style.transition = '';
    } else {
      trail.style.width = `${percent}%`;
    }
    $('.hpnum', panel).textContent = `${s.hp}/${s.max_hp}`;
    const ce = $('.ce .fill', panel);
    if (ce) {
      ce.style.width = `${s.max_ce ? (s.ce / s.max_ce) * 100 : 0}%`;
      $('.cenum', panel).textContent = `${s.ce}/${s.max_ce}`;
    }
    $('.tags', panel).innerHTML = s.tags.map((t) => `<span class="chip ${esc(t.color)}">${esc(t.text)}</span>`).join('');
    panel.classList.toggle('domain', s.tags.some((t) => t.text.startsWith('Domain')));
    panel.classList.toggle('dead', s.hp <= 0);
    if (prev !== null && prev.hp !== s.hp) {
      floater(panel, s.hp - prev.hp);
      flash(panel, s.hp < prev.hp ? 'hit' : 'heal');
    }
    battle.prev[i] = { hp: s.hp };
  });
}

function addLog(ev) {
  const log = $('#log');
  if (!log) return;
  const line = document.createElement('div');
  line.className = `entry${ev.gap ? ' gap' : ''} tone-${ev.tone}`;
  ev.segs.forEach((seg) => {
    const span = document.createElement('span');
    span.textContent = seg.t;
    if (seg.c) span.classList.add(`c-${seg.c}`);
    if (seg.b) span.classList.add('b');
    line.appendChild(span);
  });
  log.appendChild(line);
  while (log.children.length > 400) log.removeChild(log.firstChild);
  log.scrollTop = log.scrollHeight;
}

function showMoves(ev) {
  const fighter = battle.fighters[ev.who];
  battle.prompt = ev;
  const showDesc = boot.settings.show_descriptions;
  $('#movepanel').innerHTML = `
    <div class="mp-head">${avatar(fighter.name, 'sm')}<b style="color:${colorOf(fighter.name)}">${esc(ev.label)}</b>
      <span>choose your move</span><span class="sp"></span>
      <span class="hint">Keys 1-${ev.moves.length}</span>
      <button class="btn small" id="b-inspect">🔍 Inspect opponent</button></div>
    <div class="moves">${ev.moves.map((m, n) => `
      <button class="move k-${moveKind(m.label)}" data-move="${m.i}" ${m.ok ? '' : 'disabled'} title="${esc(m.desc)}">
        <span class="key">${n + 1}</span><span class="mn">${esc(m.name)}</span><span class="ml">${esc(m.label)}</span>
        <span class="mm"><span>CE ${m.ce}</span>${m.why === 'cooldown' ? `<span class="bad">Cooldown ${m.cd}</span>`
          : m.why === 'ce' ? '<span class="bad">Not enough CE</span>' : ''}</span>
        ${showDesc ? `<span class="md">${esc(m.desc)}</span>` : ''}
      </button>`).join('')}</div>`;
  $$('[data-move]', $('#movepanel')).forEach((el) => { el.onclick = () => chooseMove(+el.dataset.move); });
  $('#b-inspect').onclick = () => inspectOpponent(ev.who);
}

async function chooseMove(index) {
  if (!battle || !battle.prompt || battle.prompt.kind !== 'move') return;
  battle.prompt = null;
  setWaiting('Resolving');
  await API.post('/api/move', { index });
}

function inspectOpponent(who) {
  const opponent = battle.fighters[1 - who];
  const live = battle.prev[1 - who] ? { hp: battle.prev[1 - who].hp, max_hp: opponent.hp } : null;
  openModal(`<div class="card" style="border:0;padding:0">${cardHTML(opponent, live)}</div>`, [{ label: 'Close', cls: 'primary' }]);
}

function showRika(ev) {
  battle.prompt = ev;
  openModal('<h3>Call to Rika</h3><p>Choose one of Yuta\'s copied techniques. It costs no extra CE.</p>',
    ev.options.map((o) => ({
      label: `${o.name}   ·   ${o.label}`, cls: 'primary', close: true,
      onClick: () => { battle.prompt = null; API.post('/api/rika', { index: o.i }); },
    })), { dismiss: false, stack: true });
}

function delayFor(ev) {
  if (battle.skip) return 0;
  const base = SPEED_MS[boot.settings.text_speed] ?? SPEED_MS.normal;
  const lines = ev.segs ? ev.segs.map((s) => s.t).join('').split('\n').length : 1;
  const tone = ev.tone === 'quiet' ? 0.25 : ev.tone === 'intro' ? 2.2 : 1;
  return base * tone * (1 + 0.3 * (lines - 1));
}

async function play(b, ev) {
  switch (ev.t) {
    case 'start': buildBattle(ev); break;
    case 'turn': $('#b-turn').textContent = `Turn ${ev.n} / ${ev.max}`; break;
    case 'actor':
      $$('.fighter').forEach((el) => el.classList.toggle('active', +el.dataset.i === ev.who));
      applyState(ev.state);
      break;
    case 'log': {
      addLog(ev);
      applyState(ev.state);
      const wait = delayFor(ev);
      if (wait > 0) await sleep(wait);
      break;
    }
    case 'prompt':
      b.skip = false;
      if (ev.kind === 'move') showMoves(ev); else showRika(ev);
      break;
    case 'end': finishBattle(ev); break;
    case 'error':
      openModal(`<h3>Something went wrong</h3><p>${esc(ev.message)}</p><p>Details were saved to crash.log.</p>`,
        [{ label: 'Back to menu', cls: 'primary', onClick: () => leaveBattle(false) }], { dismiss: false });
      break;
    default: break;
  }
}

async function pump(b) {
  if (b.pumping) return;
  b.pumping = true;
  try {
    while (b.queue.length && battle === b) await play(b, b.queue.shift());
  } finally {
    b.pumping = false;
  }
}

async function pollLoop(b) {
  while (battle === b) {
    try {
      const reply = await API.get(`/api/poll?sid=${b.sid}&since=${b.since}`);
      if (battle !== b || reply.stale) return;
      b.since = reply.next;
      b.queue.push(...reply.events);
      pump(b);
      if (reply.done) return;
    } catch (error) {
      await sleep(500);
    }
  }
}

async function startMatch() {
  const names = [0, 1].map((i) => (setup.names[i] || '').trim() || `Player ${i + 1}`);
  const reply = await API.post('/api/start', { mode: setup.mode, names, picks: setup.picks });
  if (!reply.ok) { toast('Could not start the match.'); return; }
  battle = { sid: reply.sid, since: 0, queue: [], pumping: false, skip: false, prompt: null, prev: [null, null], finished: false };
  closeModal();
  show('battle');
  $('#screen-battle').innerHTML = '<div class="waiting">Loading<span class="dots"></span></div>';
  pollLoop(battle);
}

function finishBattle(ev) {
  battle.finished = true;
  $$('.fighter').forEach((el) => el.classList.remove('active'));
  setWaiting('Match over');
  const turnsText = `Match length: ${ev.turns} turn${ev.turns === 1 ? '' : 's'}`;
  const buttons = [
    { label: 'Rematch', cls: 'primary', onClick: () => startMatch() },
    { label: 'New fighters', onClick: () => { leaveBattle(false); setup.picks = [null, null]; setup.slot = 0; show('select'); } },
    { label: 'Main menu', onClick: () => leaveBattle(false) },
  ];
  if (ev.winner === null) {
    openModal(`<div class="result"><div class="big" style="color:var(--yellow)">Draw</div>
      <p>Nobody wins. The battlefield is destroyed!</p><p style="color:var(--muted)">${turnsText}</p></div>`, buttons, { cls: 'result', dismiss: false });
  } else {
    const name = ev.names[ev.winner];
    openModal(`<div class="result">${avatar(name, 'lg')}<div class="big" style="color:${colorOf(name)}">${esc(name)} wins!</div>
      <p>${esc(ev.labels[ev.winner])} takes the match.</p><p style="color:var(--muted)">${turnsText}</p></div>`, buttons, { cls: 'result', dismiss: false });
  }
}

function leaveBattle(abort = true) {
  const b = battle;
  battle = null;
  closeModal();
  if (b && abort && !b.finished) API.post('/api/abort');
  show('title');
}

function confirmLeave() {
  if (!battle || battle.finished) { leaveBattle(); return; }
  openModal('<h3>Leave this match?</h3><p>The match will end and will not count.</p>', [
    { label: 'Keep playing' },
    { label: 'Leave match', cls: 'danger', onClick: () => leaveBattle(true) },
  ]);
}

async function renderStats() {
  const root = $('#screen-stats');
  root.innerHTML = '<div class="head"><button class="btn small" data-back>&larr; Back</button><h2>Stats</h2></div><div class="empty-note">Loading...</div>';
  $('[data-back]', root).onclick = () => show('title');
  const data = await API.get('/api/stats');
  const table = (title, rows, favorite) => `
    <div class="tbl-wrap"><table><thead><tr><th>${title}</th><th>W</th><th>L</th><th>D</th><th>Win %</th>${favorite ? '<th>Favorite</th>' : ''}</tr></thead>
    <tbody>${rows.map((r) => `<tr><td>${esc(r.name)}</td><td class="n">${r.wins}</td><td class="n">${r.losses}</td><td class="n">${r.draws}</td>
      <td class="n">${r.rate}%</td>${favorite ? `<td>${esc(r.favorite)}</td>` : ''}</tr>`).join('')}</tbody></table></div>`;
  root.innerHTML = `
    <div class="head"><button class="btn small" data-back>&larr; Back</button><h2>Stats</h2><span class="sub">${data.matches} match${data.matches === 1 ? '' : 'es'} recorded</span></div>
    ${data.matches === 0
      ? '<div class="tbl-wrap"><div class="empty-note">No matches yet. Play a Human vs AI or Human vs Human game and your results will show up here.</div></div>'
      : `<div class="stats-cols">${table('Players', data.players, true)}${table('Fighters', data.fighters, false)}</div>`}`;
  $('[data-back]', root).onclick = () => show('title');
}

async function saveSetting(patch) {
  const reply = await API.post('/api/settings', patch);
  if (reply.ok) boot.settings = reply.settings;
  renderSettings();
}

function renderSettings() {
  const s = boot.settings;
  const seg = (key, options) => `<div class="seg">${options.map((o) => `<button data-key="${key}" data-val="${o}" class="${s[key] === o ? 'on' : ''}">${o[0].toUpperCase() + o.slice(1)}</button>`).join('')}</div>`;
  const toggle = (key) => `<div class="seg"><button data-key="${key}" data-val="true" class="${s[key] ? 'on' : ''}">On</button><button data-key="${key}" data-val="false" class="${!s[key] ? 'on' : ''}">Off</button></div>`;
  const root = $('#screen-settings');
  root.innerHTML = `
    <div class="head"><button class="btn small" data-back>&larr; Back</button><h2>Settings</h2></div>
    <div class="set-list">
      <div class="set-row"><div class="t"><b>Text speed</b><span>How fast the battle log plays.</span></div>${seg('text_speed', s.speeds)}</div>
      <div class="set-row"><div class="t"><b>AI difficulty</b><span>Easy plays randomly, Hard almost always picks its strongest move.</span></div>${seg('ai_difficulty', s.difficulties)}</div>
      <div class="set-row"><div class="t"><b>Move descriptions</b><span>Show what each move does on buttons and fighter cards.</span></div>${toggle('show_descriptions')}</div>
      <div class="set-row"><div class="t"><b>Pre-battle dialogue</b><span>Show the story scene before a match.</span></div>${toggle('show_dialogue')}</div>
      <div class="set-row"><div class="t"><b>Saved stats</b><span>Erase every recorded win and loss.</span></div><button class="btn danger small" id="reset-stats">Reset stats</button></div>
    </div>`;
  $('[data-back]', root).onclick = () => show('title');
  $$('[data-key]', root).forEach((el) => {
    el.onclick = () => {
      const val = el.dataset.val;
      saveSetting({ [el.dataset.key]: val === 'true' ? true : val === 'false' ? false : val });
    };
  });
  $('#reset-stats', root).onclick = () => openModal('<h3>Erase all stats?</h3><p>This cannot be undone.</p>', [
    { label: 'Cancel' },
    { label: 'Erase', cls: 'danger', onClick: async () => { await API.post('/api/stats/reset'); toast('Stats erased.'); } },
  ]);
}

function quitGame() {
  openModal('<h3>Quit the game?</h3>', [
    { label: 'Cancel' },
    { label: 'Quit', cls: 'danger', onClick: async () => {
      await API.post('/api/shutdown');
      document.body.innerHTML = '<div style="display:grid;place-items:center;height:100%;font-size:22px;color:#cfcfe6">Thanks for playing! You can close this window.</div>';
      window.close();
    } },
  ]);
}

document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT') return;
  if (current !== 'battle' || !battle) return;
  if (e.key === 'Escape') { if (!modalOpen()) confirmLeave(); return; }
  if (modalOpen()) return;
  if (/^[1-9]$/.test(e.key) && battle.prompt && battle.prompt.kind === 'move') {
    const move = battle.prompt.moves[+e.key - 1];
    if (move && move.ok) chooseMove(move.i);
  } else if (e.key === ' ' || e.key === 'Enter') {
    e.preventDefault();
    battle.skip = true;
  }
});

async function init() {
  boot = await API.get('/api/bootstrap');
  $('#version').textContent = `Version ${boot.version}`;
  $$('[data-go]').forEach((el) => { el.onclick = () => show(el.dataset.go); });
  $('#btn-quit').onclick = quitGame;
  const ping = () => API.post('/api/ping', { page: PAGE_ID }).catch(() => {});
  ping();
  setInterval(ping, 4000);
  window.addEventListener('pagehide', () => {
    fetch('/api/closing', { method: 'POST', headers: { 'X-Game': '1', 'Content-Type': 'application/json' }, body: JSON.stringify({ page: PAGE_ID }), keepalive: true }).catch(() => {});
  });
}

init();
