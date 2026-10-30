from pathlib import Path
import re,json,hashlib,zipfile
from lxml import etree
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
def el(name, **attrs):
    node = OxmlElement(name)
    for k,v in attrs.items(): node.set(qn(k), str(v))
    return node

def mathrun(text, plain=False):
    r = el('m:r')
    rp = el('m:rPr'); rp.append(el('m:sty', **{'m:val':'p' if plain else 'i'})); r.append(rp)
    wrp = el('w:rPr'); wrp.append(el('w:rFonts', **{'w:ascii':'Cambria Math','w:hAnsi':'Cambria Math','w:eastAsia':'SimSun'})); wrp.append(el('w:sz', **{'w:val':'21'})); r.append(wrp)
    t = el('m:t'); t.text = text; r.append(t)
    return r

def container(name, nodes):
    node=el(name)
    for x in nodes: node.append(x)
    return node

SYMBOLS = dict(eta='η',kappa='κ',delta='δ',alpha='α',chi='χ',rho='ρ',lambda_='λ',gamma='γ',varepsilon='ε',zeta='ζ',phi='φ',omega='ω',pi='π',Delta='Δ',cdot='·',le='≤',ge='≥',in_='∈',sum='∑')
SYMBOLS['lambda']=SYMBOLS.pop('lambda_'); SYMBOLS['in']=SYMBOLS.pop('in_')
SYMBOLS.update(xi='ξ',int='∫',leq='≤',geq='≥',beta='β',Omega='Ω')

class Latex:
    """Strict LaTeX subset to editable OMML; unsupported syntax fails before writing."""
    def __init__(self, s): self.s=s; self.i=0
    def skip(self):
        while self.i<len(self.s) and self.s[self.i].isspace(): self.i+=1
    def argument(self):
        self.skip()
        if self.i<len(self.s) and self.s[self.i]=='{':
            self.i+=1; result=self.sequence('}'); return result
        return self.atom()
    def sequence(self, stop=None):
        out=[]
        while self.i<len(self.s):
            self.skip()
            if self.i>=len(self.s): break
            if stop and self.s[self.i]==stop: self.i+=1; return out
            if self.s[self.i]=='}': raise ValueError('unmatched brace')
            base=self.atom(); self.skip(); sub=sup=None
            while self.i<len(self.s) and self.s[self.i] in '_^':
                kind=self.s[self.i]; self.i+=1; arg=self.argument()
                if kind=='_': sub=arg
                else: sup=arg
                self.skip()
            if sub is not None or sup is not None:
                text=''.join(n.text or '' for b in base for n in b.iter(qn('m:t')))
                if sub is not None and text in ['∑','min','max']:
                    x=el('m:limLow'); x.append(container('m:e',base)); x.append(container('m:lim',sub)); base=[x]; sub=None
                if sub is not None and sup is not None:
                    x=el('m:sSubSup'); x.append(container('m:e',base)); x.append(container('m:sub',sub)); x.append(container('m:sup',sup)); base=[x]
                elif sub is not None:
                    isbrace=any(n.tag==qn('m:groupChr') for b in base for n in b.iter())
                    x=el('m:limLow' if isbrace else 'm:sSub'); x.append(container('m:e',base)); x.append(container('m:lim' if isbrace else 'm:sub',sub)); base=[x]
                elif sup is not None:
                    x=el('m:sSup'); x.append(container('m:e',base)); x.append(container('m:sup',sup)); base=[x]
            out.extend(base)
        if stop: raise ValueError('unclosed '+stop)
        return out
    def atom(self):
        self.skip()
        if self.i>=len(self.s): return []
        c=self.s[self.i]; self.i+=1
        if c=='{': return self.sequence('}')
        if c!='\\': return [mathrun(c, c.isdigit() or c in '+-=(),[]|./:')]
        if self.i>=len(self.s): raise ValueError('trailing slash')
        if not self.s[self.i].isalpha():
            c=self.s[self.i]; self.i+=1
            if c in '!': return []
            if c in ',; ': return [mathrun('\u2009',True)]
            if c=='|': return [mathrun('‖',True)]
            if c in '{}': return [mathrun(c,True)]
            raise ValueError('unknown escaped '+c)
        start=self.i
        while self.i<len(self.s) and self.s[self.i].isalpha(): self.i+=1
        cmd=self.s[start:self.i]
        if cmd in ['Phi','ell','mu','sigma','theta','Gamma','Theta']:
            return [mathrun({'Phi':'Φ','ell':'ℓ','mu':'μ','sigma':'σ','theta':'θ','Gamma':'Γ','Theta':'Θ'}[cmd])]
        if cmd in ['sin','cos','tan','diag','sgn']: return [mathrun(cmd,True)]
        if cmd in ['left','right']:
            self.skip()
            if self.i < len(self.s) and self.s[self.i]=='.': self.i+=1; return []
            return self.atom()
        if cmd=='begin':
            self.skip()
            if self.s[self.i]!='{': raise ValueError('missing environment')
            end=self.s.index('}',self.i); env=self.s[self.i+1:end]; self.i=end+1
            if env not in ['cases','matrix','pmatrix','bmatrix']: raise ValueError('unsupported environment '+env)
            marker='\\end{'+env+'}'; end=self.s.index(marker,self.i)
            body=self.s[self.i:end]; self.i=end+len(marker)
            rows=[x for x in re.split(r'\\\\',body) if x.strip()]
            matrix=el('m:m')
            for row in rows:
                mr=el('m:mr')
                for cell in row.split('&'): mr.append(container('m:e',Latex(cell).sequence()))
                matrix.append(mr)
            if env=='matrix': return [matrix]
            d=el('m:d'); pr=el('m:dPr')
            beg,fin={'cases':('{',''),'pmatrix':('(',')'),'bmatrix':('[',']')}[env]
            pr.append(el('m:begChr',**{'m:val':beg}));pr.append(el('m:endChr',**{'m:val':fin}))
            d.append(pr);d.append(container('m:e',[matrix]));return [d]
        if cmd in SYMBOLS: return [mathrun(SYMBOLS[cmd],cmd in ['sum','cdot','le','ge','in'])]
        if cmd in ['min','max']: return [mathrun(cmd,True)]
        if cmd in ['quad','qquad']: return [mathrun('\u2003',True)]
        if cmd=='sqrt':
            x=el('m:rad');pr=el('m:radPr');pr.append(el('m:degHide',**{'m:val':'1'}));x.append(pr)
            x.append(el('m:deg'));x.append(container('m:e',self.argument()));return [x]
        if cmd=='frac':
            a=self.argument(); b=self.argument(); x=el('m:f'); x.append(container('m:num',a)); x.append(container('m:den',b)); return [x]
        if cmd in ['dot','ddot','widehat']:
            x=el('m:acc'); p=el('m:accPr'); p.append(el('m:chr',**{'m:val':{'dot':'\u0307','ddot':'\u0308','widehat':'\u0302'}[cmd]})); x.append(p); x.append(container('m:e',self.argument())); return [x]
        if cmd in ['operatorname','mathrm','text','boldsymbol','mathcal','mathbf']:
            nodes=self.argument()
            for node in nodes:
                for r in node.iter(qn('m:r')):
                    rp=r.find(qn('m:rPr'))
                    if rp is None: rp=el('m:rPr');r.insert(0,rp)
                    for old in list(rp): rp.remove(old)
                    if cmd=='mathcal': rp.append(el('m:scr',**{'m:val':'script'})); rp.append(el('m:sty',**{'m:val':'p'}))
                    else: rp.append(el('m:sty',**{'m:val':'bi' if cmd=='boldsymbol' else ('b' if cmd=='mathbf' else 'p')}))
            return nodes
        if cmd=='underbrace':
            x=el('m:groupChr'); p=el('m:groupChrPr'); p.append(el('m:chr',**{'m:val':'\u23df'})); p.append(el('m:pos',**{'m:val':'bot'})); p.append(el('m:vertJc',**{'m:val':'bot'})); x.append(p); x.append(container('m:e',self.argument())); return [x]
        raise ValueError('unsupported command '+cmd)

def parse_math(s):
    parser=Latex(s); nodes=parser.sequence(); assert parser.i==len(s); return nodes


