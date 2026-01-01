# IDOARRT Format Specification

IDOARRT är ett ramverk för att strukturera möten och säkerställa att de har tydliga mål och roller.

## Format Overview

En IDOARRT-fil är en markdown-fil med sex obligatoriska sektioner:

1. **I**ntent (Syfte)
2. **D**esired **O**utcomes (Önskade resultat)
3. **A**genda (Dagordning)
4. **R**oles (Roller)
5. **R**ules (Regler)
6. **T**ime (Tid)

## Detailed Specification

### Intent

**Format**: En enda rad text som beskriver varför mötet hålls.

```markdown
# Intent
Diskutera och besluta om nästa kvartals produktstrategi
```

### Desired Outcomes

**Format**: En punktlista med konkreta, mätbara resultat som mötet ska uppnå.

```markdown
# Desired Outcomes
- Beslutat om 3 prioriterade funktioner för Q2
- Överenskommelse om resurstilldelning mellan teamen
- Tydlig plan för nästa steg med deadlines
```

### Agenda

**Format**: En numrerad lista där varje punkt har ett ämne och en tidsallokering i minuter.

**Viktigt**: Tidsallokeringarna måste summera till den totala mötestiden.

```markdown
# Agenda
1. Introduktion och mötets syfte (5 min)
2. Genomgång av Q1-resultat (15 min)
3. Brainstorming: Q2-prioriteringar (20 min)
4. Diskussion och beslut (15 min)
5. Sammanfattning och nästa steg (5 min)
```

### Roles

**Format**: En punktlista med roller och vem som har dem.

```markdown
# Roles
- Facilitator: Anna Andersson
- Timekeeper: Björn Berg
- Notetaker: Clara Carlsson
```

### Rules

**Format**: En punktlista med spelregler för mötet.

```markdown
# Rules
- Mobiler på ljudlöst läge
- En person i taget pratar
- Håll dig till ämnet - använd "parkering" för sidospår
- Var konstruktiv och lösningsfokuserad
```

### Time

**Format**: Total mötestid i minuter.

```markdown
# Time
Total: 60 minutes
```

## Validation Rules

Systemet validerar följande:

1. ✅ Alla sex sektioner måste finnas
2. ✅ Intent får inte vara tom
3. ✅ Desired Outcomes måste ha minst 1 punkt
4. ✅ Agenda måste ha minst 1 punkt
5. ✅ Varje agenda-punkt måste ha tidsallokering
6. ✅ Summan av agenda-tider måste matcha Total tid
7. ✅ Roles måste ha minst 1 roll definierad
8. ✅ Rules måste ha minst 1 regel
9. ✅ Total tid måste vara ett positivt heltal

## Complete Example

```markdown
# Intent
Planera och fördela arbete för Sprint 12

# Desired Outcomes
- Alla user stories estimerade och prioriterade
- Sprint backlog klar med 20 story points
- Teammedlemmar har tydliga uppgifter
- Identifierade risker och dependencies

# Agenda
1. Sprint review av Sprint 11 (10 min)
2. Genomgång av produktbacklog (15 min)
3. Story estimation (poker planning) (20 min)
4. Sprint planning och kapacitet (10 min)
5. Uppgiftsfördelning (10 min)
6. Risker och dependencies (5 min)
7. Sammanfattning (5 min)

# Roles
- Scrum Master: Emma Eriksson
- Product Owner: Fredrik Falk
- Timekeeper: Gustav Gustavsson
- Notetaker: Helena Holm

# Rules
- Timeboxed estimations - max 2 minuter per story
- Konsensus vid estimering - använd planning poker
- Fokusera på värde för kunden
- Flagga blockers direkt
- Respektera kapacitetsgränser

# Time
Total: 75 minutes
```

## Common Mistakes

### ❌ Tiderna summerar inte till totalen

```markdown
# Agenda
1. Intro (10 min)
2. Diskussion (30 min)

# Time
Total: 60 minutes  ← FEL! 10 + 30 = 40, inte 60
```

### ❌ Ingen tidsallokering på agenda-punkter

```markdown
# Agenda
1. Intro
2. Diskussion  ← FEL! Ingen tidsangivelse
```

### ❌ Intent är för vag

```markdown
# Intent
Ha ett möte  ← FEL! För vagt, säg VARFÖR
```

Bättre:
```markdown
# Intent
Lösa kommunikationsproblemen mellan utvecklings- och designteamet
```

### ❌ Desired Outcomes är aktiviteter, inte resultat

```markdown
# Desired Outcomes
- Diskutera buggen  ← FEL! Detta är en aktivitet, inte ett resultat
```

Bättre:
```markdown
# Desired Outcomes
- Identifierad grundorsak till buggen
- Beslutad fix-strategi med ansvarig
- Tidsplan för deploy av fix
```

## Tips för Bra IDOARRT

1. **Specifikt Intent**: Säg exakt VARFÖR mötet behövs
2. **Mätbara Outcomes**: Var konkret om vad ni vill uppnå
3. **Realistisk Agenda**: Var ärlig om hur lång tid saker tar
4. **Tydliga Roller**: Välj personer som kan fylla rollerna
5. **Genomtänkta Regler**: Anpassa till mötets behov och kultur

## Using with Meeting Facilitator

När du laddar upp en IDOARRT-fil till Meeting Facilitator kommer systemet att:

1. **Parse** filen och extrahera all strukturerad data
2. **Validera** att alla regler följs
3. **Visa** en preview där du kan verifiera att allt är korrekt
4. **Använda** denna data för att:
   - Tidshantering (varningar vid 50%, 75%, 5min kvar)
   - Målfokusering (detektera när diskussionen spårar ur)
   - Facilitation (generera relevanta coaching-frågor)
   - Protokoll (sammanfatta per agenda-punkt och desired outcome)

## Template

Kopiera och anpassa denna mall:

```markdown
# Intent
[Varför håller vi detta möte?]

# Desired Outcomes
- [Konkret, mätbart resultat 1]
- [Konkret, mätbart resultat 2]
- [Konkret, mätbart resultat 3]

# Agenda
1. [Ämne 1] ([X] min)
2. [Ämne 2] ([Y] min)
3. [Ämne 3] ([Z] min)

# Roles
- Facilitator: [Namn]
- Timekeeper: [Namn]
- Notetaker: [Namn]

# Rules
- [Regel 1]
- [Regel 2]
- [Regel 3]

# Time
Total: [X+Y+Z] minutes
```
