<script setup>
import { ref, computed } from 'vue'

const advanced = ref(false)
const query = ref('')
const rank = ref('occurrences')
const scope = ref('index')
const loading = ref(false)
const error = ref('')
const data = ref(null)
const excerpt = ref(null)

const placeholder = computed(() =>
  advanced.value ? 'Expression régulière, par exemple sa(l|g)on' : 'Un mot, par exemple whale')

async function run() {
  if (!query.value.trim()) return
  loading.value = true
  error.value = ''
  excerpt.value = null
  const params = new URLSearchParams({ rank: rank.value })
  let url
  if (advanced.value) {
    params.set('regex', query.value.trim())
    params.set('scope', scope.value)
    url = '/api/search/advanced/?' + params
  } else {
    params.set('q', query.value.trim())
    url = '/api/search/?' + params
  }
  try {
    const res = await fetch(url)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Erreur du serveur')
    data.value = json
  } catch (e) {
    data.value = null
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function open(book) {
  fetch(`/api/book/${book.id}/click/`, { method: 'POST' })
  const res = await fetch(`/api/book/${book.id}/text/?n=2500`)
  excerpt.value = { ...book, text: (await res.json()).excerpt }
}
</script>

<template>
  <main>
    <header>
      <h1>Bibliothèque</h1>
      <p class="lede">Cherchez un mot ou une expression régulière dans les livres du corpus.</p>
    </header>

    <form @submit.prevent="run" role="search">
      <div class="modes" role="group" aria-label="Type de recherche">
        <button type="button" :class="{ on: !advanced }" @click="advanced = false">Mot-clé</button>
        <button type="button" :class="{ on: advanced }" @click="advanced = true">Expression régulière</button>
      </div>
      <div class="row">
        <input v-model="query" :placeholder="placeholder" aria-label="Recherche" autofocus />
        <button class="go" type="submit" :disabled="loading">{{ loading ? 'Recherche…' : 'Rechercher' }}</button>
      </div>
      <div class="opts">
        <label>Classer par
          <select v-model="rank">
            <option value="occurrences">occurrences</option>
            <option value="pagerank">PageRank</option>
            <option value="closeness">closeness</option>
          </select>
        </label>
        <label v-if="advanced">Chercher dans
          <select v-model="scope">
            <option value="index">l'index (rapide)</option>
            <option value="content">le texte complet (lent)</option>
          </select>
        </label>
      </div>
    </form>

    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <section v-if="data">
      <h2>{{ data.count }} livre{{ data.count > 1 ? 's' : '' }} trouvé{{ data.count > 1 ? 's' : '' }}</h2>
      <p v-if="!data.count" class="muted">Aucun résultat. Essayez un autre mot ou élargissez l'expression.</p>
      <ol class="results">
        <li v-for="b in data.results" :key="b.id">
          <button class="title" @click="open(b)">{{ b.title }}</button>
          <span class="meta">{{ b.author || 'Auteur inconnu' }}, {{ b.language }}</span>
          <span class="score">{{ b.occurrences }} occurrence{{ b.occurrences > 1 ? 's' : '' }}</span>
        </li>
      </ol>

      <div v-if="data.suggestions.length" class="suggest">
        <h3>Dans le même esprit</h3>
        <ul>
          <li v-for="s in data.suggestions" :key="s.id">
            <button class="title" @click="open(s)">{{ s.title }}</button>
            <span class="meta">{{ s.author }}</span>
          </li>
        </ul>
      </div>
    </section>

    <aside v-if="excerpt" class="excerpt">
      <button class="close" @click="excerpt = null" aria-label="Fermer l'extrait">Fermer</button>
      <h3>{{ excerpt.title }}</h3>
      <pre>{{ excerpt.text }}</pre>
    </aside>
  </main>
</template>

<style scoped>
main { max-width: 760px; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }
h1 { font-size: 2.4rem; margin: 0 0 .25rem; }
.lede { color: var(--muted); margin: 0 0 2rem; }
.modes { display: inline-flex; border: 1px solid var(--rule); border-radius: 6px; overflow: hidden; margin-bottom: .75rem; }
.modes button { border: 0; background: var(--paper); padding: .45rem .9rem; cursor: pointer; color: var(--ink); }
.modes button.on { background: var(--accent); color: #fff; }
.row { display: flex; gap: .5rem; }
.row input { flex: 1; padding: .65rem .8rem; border: 1px solid var(--ink); border-radius: 6px; }
.go { padding: .65rem 1.1rem; border: 1px solid var(--accent); background: var(--accent); color: #fff; border-radius: 6px; cursor: pointer; }
.go:disabled { opacity: .6; cursor: wait; }
.opts { display: flex; gap: 1.25rem; flex-wrap: wrap; margin-top: .75rem; color: var(--muted); font-size: .9rem; }
.opts select { margin-left: .35rem; padding: .2rem .3rem; }
.error { color: var(--error); margin-top: 1rem; }
.muted { color: var(--muted); }
section { margin-top: 2.25rem; }
h2 { font-size: 1.3rem; margin: 0 0 .75rem; }
.results, .suggest ul { list-style: none; padding: 0; margin: 0; }
.results li, .suggest li { display: grid; grid-template-columns: 1fr auto; gap: .1rem 1rem; padding: .7rem 0; border-top: 1px solid var(--rule); }
.title { grid-column: 1; text-align: left; background: none; border: 0; padding: 0; color: var(--accent); font-weight: 600; cursor: pointer; }
.title:hover { text-decoration: underline; }
.meta { grid-column: 1; color: var(--muted); font-size: .9rem; }
.score { grid-column: 2; grid-row: 1 / span 2; align-self: center; font-size: .9rem; }
.suggest { margin-top: 2rem; padding-top: .5rem; }
.suggest h3 { font-size: 1.1rem; margin: 0 0 .5rem; }
.suggest li { grid-template-columns: 1fr; }
.excerpt { margin-top: 2rem; padding: 1rem 1.25rem; background: var(--accent-soft); border-left: 3px solid var(--accent); }
.excerpt pre { white-space: pre-wrap; font: .85rem/1.55 Georgia, serif; max-height: 22rem; overflow: auto; }
.close { float: right; background: none; border: 1px solid var(--rule); border-radius: 6px; padding: .25rem .6rem; cursor: pointer; }
</style>
