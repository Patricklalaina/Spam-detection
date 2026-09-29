import { useEffect, useState } from 'react'
import { getInfo, predict } from './lib/api.js'

const EXEMPLES = {
  'Message promotionnel':
    'congratulations you have been selected to receive a free iphone click the link below to claim your prize now limited offer act fast',
  'Message ordinaire':
    'hi could you review the patch i sent yesterday i fixed the typo in the readme and rebased on master let me know if anything looks off',
}

const pct = (n) => n.toFixed(1).replace('.', ',')

export default function App() {
  const [info, setInfo] = useState(null)
  const [horsLigne, setHorsLigne] = useState(false)
  const [texte, setTexte] = useState('')
  const [resultat, setResultat] = useState(null)
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    getInfo().then(setInfo).catch(() => setHorsLigne(true))
  }, [])

  const analyser = async () => {
    if (enCours) return
    if (!texte.trim()) return setResultat({ etat: 'vide' })
    setEnCours(true)
    try {
      const r = await predict(texte)
      setResultat(r.known ? { etat: 'ok', ...r } : { etat: 'inconnu' })
    } catch {
      setResultat({ etat: 'erreur' })
    } finally {
      setEnCours(false)
    }
  }

  const surClavier = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) analyser()
  }

  const nTrain = info?.nTrain.toLocaleString('fr-FR')

  return (
    <main className="mx-auto max-w-2xl px-5 py-14 sm:py-20">
      <h1 className="text-4xl font-semibold tracking-tight">Détecteur de spam</h1>
      <p className="mt-3 max-w-prose leading-relaxed text-doux">
        {info
          ? `Naive Bayes multinomial sur vecteurs tf-idf, entraîné sur ${nTrain} messages — ${pct(info.accuracy * 100)} % de justesse en validation.`
          : 'Naive Bayes multinomial sur vecteurs tf-idf.'}{' '}
        Le message est envoyé à l’API pour analyse ; il n’est pas conservé.
      </p>

      <div className="mt-10">
        <label htmlFor="message" className="mb-2 block text-sm font-medium">
          Message à analyser
        </label>
        <textarea
          id="message"
          value={texte}
          onChange={(e) => setTexte(e.target.value)}
          onKeyDown={surClavier}
          rows={8}
          placeholder="Collez ici le contenu d’un e-mail…"
          className="w-full resize-y rounded-xl border border-bordure bg-surface p-4 leading-relaxed text-texte placeholder:text-doux focus:border-doux focus:outline-none"
        />

        <div className="mt-4 flex flex-wrap gap-2">
          {Object.entries(EXEMPLES).map(([nom, contenu]) => (
            <button
              key={nom}
              type="button"
              onClick={() => {
                setTexte(contenu)
                setResultat(null)
              }}
              className="rounded-full border border-bordure px-4 py-2 text-sm text-texte transition-colors hover:bg-surface focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-texte"
            >
              {nom}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={analyser}
          disabled={horsLigne || enCours}
          className="mt-6 rounded-full bg-texte px-6 py-2.5 text-sm font-semibold text-fond transition-opacity hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-texte disabled:opacity-40"
        >
          {horsLigne ? 'Serveur injoignable' : enCours ? 'Analyse en cours…' : 'Analyser'}
        </button>
      </div>

      <div aria-live="polite">{resultat && <Resultat r={resultat} />}</div>

      <p className="mt-12 border-t border-bordure pt-5 text-sm leading-relaxed text-doux">
        Le rouge signale les termes qui tirent vers le spam, le vert ceux qui tirent vers un
        message sain. Le modèle a été entraîné sur des e-mails en anglais : les textes dans une
        autre langue sont jugés sur peu d’indices.
      </p>
    </main>
  )
}

function Resultat({ r }) {
  if (r.etat !== 'ok') {
    const msg = {
      vide: 'Saisissez un message à analyser.',
      inconnu: 'Aucun terme de ce message n’est connu du modèle. Essayez un texte plus long, en anglais.',
      erreur: 'Le serveur d’analyse ne répond pas. Vérifiez que l’API est démarrée, puis réessayez.',
    }[r.etat]
    return <Carte><p className="text-doux">{msg}</p></Carte>
  }

  const spam = r.pSpam >= 0.5
  const confiance = (spam ? r.pSpam : 1 - r.pSpam) * 100
  const max = Math.max(...r.terms.map((t) => Math.abs(t.weight)))

  return (
    <Carte>
      <div className="flex items-baseline justify-between gap-4">
        <h2 className={`text-3xl font-semibold tracking-tight ${spam ? 'text-spam' : 'text-sain'}`}>
          {spam ? 'Spam' : 'Message sain'}
        </h2>
        <p className="text-sm text-doux">{pct(confiance)} % de confiance</p>
      </div>

      <div
        role="meter"
        aria-label="Probabilité de spam"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(r.pSpam * 100)}
        className="relative mt-5 h-1.5 rounded-full bg-bordure"
      >
        <div
          className={`h-full rounded-full ${spam ? 'bg-spam' : 'bg-sain'}`}
          style={{ width: `${r.pSpam * 100}%` }}
        />
        <div className="absolute -top-1 bottom-[-4px] left-1/2 w-px bg-doux" aria-hidden="true" />
      </div>
      <div className="mt-2 flex justify-between text-xs text-doux">
        <span>Message sain</span>
        <span>Spam</span>
      </div>

      <h3 className="mt-8 text-sm font-medium">Termes décisifs</h3>
      <ul className="mt-3 space-y-2.5">
        {r.terms.map((t) => (
          <li key={t.word} className="grid grid-cols-[minmax(0,8rem)_1fr] items-center gap-4 text-sm">
            <span className="truncate">{t.word}</span>
            <span className="h-1.5 rounded-full bg-bordure">
              <span
                className={`block h-full rounded-full ${t.weight > 0 ? 'bg-spam' : 'bg-sain'}`}
                style={{ width: `${Math.max(4, (Math.abs(t.weight) / max) * 100)}%` }}
              />
            </span>
          </li>
        ))}
      </ul>
    </Carte>
  )
}

function Carte({ children }) {
  return <section className="mt-8 rounded-2xl border border-bordure bg-surface p-6">{children}</section>
}
