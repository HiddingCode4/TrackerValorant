"""Transparent descriptive statistics; never a cheating verdict."""
import math

FIELDS = ('kills', 'deaths', 'assists', 'rounds', 'damage', 'score', 'headshots', 'bodyshots', 'legshots')

def validate(data):
    if not isinstance(data, dict) or not isinstance(data.get('matches'), list):
        raise ValueError('Le fichier doit contenir une liste matches.')
    if len(data['matches']) > 500:
        raise ValueError('Maximum 500 matchs par fichier.')
    for m in data['matches']:
        if not isinstance(m, dict):
            raise ValueError('Match invalide.')
        for field in FIELDS:
            v = m.get(field)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
                raise ValueError(f'Champ invalide : {field}')
        if m['rounds'] < 1:
            raise ValueError('Chaque match doit avoir au moins un round.')
    return data

def summarize(data):
    validate(data)
    matches = data['matches'][:10]  # Contract: newest first.
    n = len(matches)
    total = {f: sum(m[f] for m in matches) for f in FIELDS}
    rounds = total['rounds']
    hits = total['headshots'] + total['bodyshots'] + total['legshots']
    result = dict(count=n, kd=total['kills']/max(1,total['deaths']),
                  adr=total['damage']/rounds if rounds else 0,
                  acs=total['score']/rounds if rounds else 0,
                  hs=100*total['headshots']/hits if hits else None,
                  wins=sum(m.get('result') == 'win' for m in matches), signals=[])
    if n < 10:
        result['signals'].append(f'Données insuffisantes : {n}/10 matchs. Aucune conclusion de profil.')
        return result
    dominant = sum(m['kills']/max(1,m['deaths']) >= 1.5 and m['score']/m['rounds'] >= 280 for m in matches)
    if dominant >= 6:
        result['signals'].append(f'Domination régulière : {dominant}/10 matchs avec K/D ≥ 1,5 et ACS ≥ 280.')
    recent = sum(m['score']/m['rounds'] for m in matches[:5])/5
    older = sum(m['score']/m['rounds'] for m in matches[5:])/5
    if older > 0 and recent >= older*1.4:
        result['signals'].append(f'Hausse d’ACS : {older:.0f} → {recent:.0f} entre les deux groupes de 5 matchs.')
    if not result['signals']:
        result['signals'].append('Aucun seuil descriptif atteint sur cet échantillon.')
    result['signals'].append('Ces observations ne confirment ni un smurf ni une triche. Seuils exploratoires non calibrés par rang.')
    return result
