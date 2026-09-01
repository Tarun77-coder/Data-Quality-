from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Literal
import math, random
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest

app=FastAPI(title='AERIS-X API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
class Observation(BaseModel):
    station_id:str; timestamp:datetime; temperature:float; pressure:float; humidity:float
class SimulationRequest(BaseModel):
    station_id:str='TN-042'; scenario:Literal['normal','temperature_spike','humidity_freeze','pressure_drift','communication_drop','genuine_weather_event']='temperature_spike'; steps:int=Field(default=20,ge=5,le=120)
STATIONS=[{'id':'TN-042','name':'Chennai Coastal AWS','lat':13.0827,'lon':80.2707,'region':'Tamil Nadu','status':'healthy'},{'id':'KA-018','name':'Bengaluru Urban AWS','lat':12.9716,'lon':77.5946,'region':'Karnataka','status':'healthy'},{'id':'MH-031','name':'Pune Plateau AWS','lat':18.5204,'lon':73.8567,'region':'Maharashtra','status':'healthy'},{'id':'AS-011','name':'Guwahati Valley AWS','lat':26.1445,'lon':91.7362,'region':'Assam','status':'warning'},{'id':'RJ-007','name':'Jaipur Arid AWS','lat':26.9124,'lon':75.7873,'region':'Rajasthan','status':'healthy'},{'id':'WB-022','name':'Kolkata Delta AWS','lat':22.5726,'lon':88.3639,'region':'West Bengal','status':'healthy'},{'id':'KL-019','name':'Kochi Humid AWS','lat':9.9312,'lon':76.2673,'region':'Kerala','status':'healthy'}]
OBS={}; ANOMALIES=[]; HEALTH={}
def dewpoint(t,rh):
    a,b=17.27,237.7; gamma=a*t/(b+t)+math.log(max(rh,1e-3)/100); return b*gamma/(a-gamma)
def rz(v,h):
    if len(h)<5:return 0.0
    a=np.asarray(h[-60:],float); med=np.median(a); mad=np.median(np.abs(a-med)); return 0.0 if mad<1e-6 else abs(0.6745*(v-med)/mad)
def analyze(o,history):
    h=history[-60:]; prev=h[-1] if h else None; dt=max((o.timestamp-prev.timestamp).total_seconds()/60 if prev else 5,1)
    dT=(o.temperature-prev.temperature)/dt if prev else 0; dP=(o.pressure-prev.pressure)/dt if prev else 0; dRH=(o.humidity-prev.humidity)/dt if prev else 0
    tz,pz,hz=rz(o.temperature,[x.temperature for x in h]),rz(o.pressure,[x.pressure for x in h]),rz(o.humidity,[x.humidity for x in h])
    rate=max(abs(dT)/1.5,abs(dP)/1.5,abs(dRH)/8)
    frozen=0.0
    if len(h)>=6:
        for f in ('temperature','pressure','humidity'):
            if max(getattr(x,f) for x in h[-6:])-min(getattr(x,f) for x in h[-6:])<1e-4:frozen=1.0
    iso=0.0
    if len(h)>=20:
        X=np.array([[x.temperature,x.pressure,x.humidity] for x in h]); m=IsolationForest(n_estimators=80,contamination=.05,random_state=42).fit(X); iso=max(0.0,float(-m.decision_function([[o.temperature,o.pressure,o.humidity]])[0]))
    if h:
        exp_t=.35*(h[-1].temperature+dT*5)+.65*np.median([x.temperature for x in h]); exp_p=.35*(h[-1].pressure+dP*5)+.65*np.median([x.pressure for x in h]); exp_r=.35*(h[-1].humidity+dRH*5)+.65*np.median([x.humidity for x in h])
    else: exp_t,exp_p,exp_r=o.temperature,o.pressure,o.humidity
    res={'temperature':o.temperature-exp_t,'pressure':o.pressure-exp_p,'humidity':o.humidity-exp_r}; active=sum(abs(v)>(.9 if k=='temperature' else 1.2 if k=='pressure' else 5) for k,v in res.items()); coherent=active>=2 and not(tz>4 and pz<1 and hz<1)
    parts=[min(tz/4,1),min(pz/4,1),min(hz/4,1),min(rate/3,1),frozen,min(iso/.35,1)]; score=round(100*float(np.average(parts,weights=[1.2,.8,.9,1,1.2,1])),1); anomaly=score>=42 or frozen>=1
    if frozen: typ,diag,reason='frozen_sensor','LIKELY SENSOR FAULT','A sensor value has remained effectively unchanged while station context continues to evolve.'; mags={f:max(getattr(x,f) for x in h[-6:])-min(getattr(x,f) for x in h[-6:]) for f in ('temperature','pressure','humidity')}; fault=min(mags,key=mags.get) if h else 'humidity'
    elif anomaly and not coherent:
        mags={'temperature':tz,'pressure':pz,'humidity':hz}; fault=max(mags,key=mags.get); typ,diag='contextual_sensor_fault','LIKELY SENSOR FAULT'; reason=f'{fault.capitalize()} deviation is not supported by the other atmospheric variables.'
    elif anomaly and coherent: fault=None; typ,diag='coherent_atmospheric_event','LIKELY GENUINE WEATHER EVENT'; reason='Temperature, pressure and humidity moved coherently enough to suggest an atmospheric event rather than an isolated sensor fault.'
    else: fault=None; typ,diag='normal','NO ACTION'; reason='Observation is within the station behavioral envelope.'
    conf=round(min(99.7,65+abs(score-50)*.65+(8 if coherent else 0)),1); sev='critical' if score>=78 else 'high' if score>=60 else 'medium' if score>=42 else 'low'; health=round(max(1,100-score*.75),1)
    return {'score':score,'is_anomaly':anomaly,'severity':sev,'anomaly_type':typ,'diagnosis':diag,'confidence':conf,'reason':reason,'fault_sensor':fault,'coherent':coherent,'observed':{'temperature':o.temperature,'pressure':o.pressure,'humidity':o.humidity},'expected':{'temperature':round(exp_t,2),'pressure':round(exp_p,2),'humidity':round(exp_r,2)},'residuals':{k:round(v,2) for k,v in res.items()},'features':{'temperature_z':round(tz,2),'pressure_z':round(pz,2),'humidity_z':round(hz,2),'rate_score':round(rate,2),'isolation_score':round(iso,3)},'recommended_action':f'Inspect {fault} sensor and mounting/telemetry path.' if fault else ('Review event against external weather context.' if coherent else 'No action required.'),'health_score':health,'dew_point':round(dewpoint(o.temperature,o.humidity),2)}
def seed():
    if OBS:return
    now=datetime.now(timezone.utc); random.seed(42)
    for j,s in enumerate(STATIONS):
        seq=[]
        for i in range(120):
            ts=now-timedelta(minutes=(119-i)*5); t=29-j*1.1+2.3*math.sin(i/14)+random.gauss(0,.18); p=1008+j*1.4+3.2*math.sin(i/22+.4)+random.gauss(0,.18); r=62+j*2+7*math.cos(i/18+.7)+random.gauss(0,.7); seq.append(Observation(station_id=s['id'],timestamp=ts,temperature=t,pressure=p,humidity=max(10,min(98,r))))
        OBS[s['id']]=seq; HEALTH[s['id']]=analyze(seq[-1],seq[:-1])['health_score']
seed()
@app.get('/health')
def health():return {'status':'ok','service':'aeris-x-api'}
@app.get('/api/stations')
def stations():return [{**s,'health_score':HEALTH.get(s['id'],96),'anomaly_count':sum(a['station_id']==s['id'] for a in ANOMALIES)} for s in STATIONS]
@app.get('/api/stations/{station_id}')
def station(station_id):
    if station_id not in OBS:raise HTTPException(404,'Station not found')
    return {'station':next(s for s in STATIONS if s['id']==station_id),'observations':[o.model_dump(mode='json') for o in OBS[station_id][-48:]],'health_score':HEALTH[station_id]}
@app.post('/api/anomaly/analyze')
def analyze_api(o:Observation):
    h=OBS.setdefault(o.station_id,[]); r=analyze(o,h); h.append(o); HEALTH[o.station_id]=r['health_score']
    if r['is_anomaly']:ANOMALIES.insert(0,{'id':f'AX-{len(ANOMALIES)+1:04d}','station_id':o.station_id,'timestamp':o.timestamp.isoformat(),**r})
    return r
@app.get('/api/anomalies')
def anomalies(limit:int=20):return ANOMALIES[:max(1,min(limit,100))]
@app.get('/api/dashboard/summary')
def summary():
    crit=sum(a['severity'] in ('critical','high') for a in ANOMALIES); return {'network_health':round(sum(HEALTH.values())/len(HEALTH),1),'stations_total':len(STATIONS),'stations_online':len(STATIONS),'anomalies_24h':len(ANOMALIES),'critical_alerts':crit}
@app.post('/api/simulate')
def simulate(req:SimulationRequest):
    if req.station_id not in OBS:raise HTTPException(404,'Station not found')
    base=OBS[req.station_id][-1]; out=[]
    for i in range(1,req.steps+1):
        ts=base.timestamp+timedelta(minutes=5*i); t,p,r=base.temperature,base.pressure,base.humidity
        if req.scenario=='temperature_spike':t+=.25*i if i<7 else 1.9+random.uniform(-.1,.1)
        elif req.scenario=='pressure_drift':p+=i*.18
        elif req.scenario=='genuine_weather_event':t+=math.sin(i/2.2);p-=1.7+.35*i;r+=3.8+1.1*i
        elif req.scenario=='communication_drop' and i>=req.steps//2:break
        ob=Observation(station_id=req.station_id,timestamp=ts,temperature=t,pressure=p,humidity=max(5,min(99,r)))
        out.append(analyze_api(ob))
    return {'scenario':req.scenario,'station_id':req.station_id,'results':out,'latest':out[-1] if out else None}
