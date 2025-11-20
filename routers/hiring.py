from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

# from ..deps import require_manager_or_admin
from ..deps import require_admin
from ..db import get_session
from ..models import User, Candidate, CandidateStage

# Define the pipeline transitions
ALLOWED_TRANSITIONS = {
    CandidateStage.APPLIED: [
        CandidateStage.SCREENING,
        CandidateStage.REJECTED,
    ],
    CandidateStage.SCREENING: [
        CandidateStage.INTERVIEW,
        CandidateStage.BACKGROUND,  # if you skip interview
        CandidateStage.REJECTED,
    ],
    CandidateStage.INTERVIEW: [
        CandidateStage.BACKGROUND,
        CandidateStage.OFFER,
        CandidateStage.REJECTED,
    ],
    CandidateStage.BACKGROUND: [
        CandidateStage.OFFER,
        CandidateStage.REJECTED,
    ],
    CandidateStage.OFFER: [
        CandidateStage.HIRED,
        CandidateStage.REJECTED,
    ],
    CandidateStage.HIRED: [],
    CandidateStage.REJECTED: [],
}

router = APIRouter(prefix="/hiring", tags=["hiring"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
def hiring_pipeline(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    candidates = session.exec(select(Candidate)).all()

    # Group by stage (if you still want the column view)
    by_stage = {stage: [] for stage in CandidateStage}
    for c in candidates:
        by_stage[c.stage].append(c)

    # Build a dict of allowed transitions using .name so Jinja can use it easily
    transitions = {
        stage.name: [next_stage.name for next_stage in next_stages]
        for stage, next_stages in ALLOWED_TRANSITIONS.items()
    }

    return templates.TemplateResponse(
        "hiring.html",
        {
            "request": request,
            "user": user,
            "by_stage": by_stage,
            "candidates": candidates,
            "transitions": transitions,
        },
    )

@router.get("/new")
def new_candidate_page(
    request: Request,
    user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        "candidate_new.html",
        {"request": request, "user": user},
    )


@router.post("/new")
def create_candidate(
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
    full_name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    position: str = Form(""),
    source: str = Form(""),
    notes: str = Form(""),
):
    c = Candidate(
        full_name=full_name,
        email=email or None,
        phone=phone or None,
        position=position or None,
        source=source or None,
        notes=notes or None,
    )
    session.add(c)
    session.commit()
    return RedirectResponse("/hiring", status_code=303)

@router.get("/{candidate_id}")
def view_candidate(
    candidate_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    candidate = session.get(Candidate, candidate_id)
    if not candidate:
        # Or raise HTTPException(404, "Candidate not found")
        return RedirectResponse("/hiring", status_code=303)

    # Allowed next stages for this one candidate
    allowed_next = ALLOWED_TRANSITIONS.get(candidate.stage, [])
    next_stage_names = [s.name for s in allowed_next]

    return templates.TemplateResponse(
        "hiring_detail.html",
        {
            "request": request,
            "user": user,
            "candidate": candidate,
            "next_stages": next_stage_names,
        },
    )

@router.post("/{candidate_id}/stage")
def update_candidate_stage(
    candidate_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
    stage: str = Form(...),
):
    candidate = session.get(Candidate, candidate_id)
    if candidate and stage in CandidateStage.__members__:
        next_stage = CandidateStage[stage]
        # Optional: enforce allowed transitions
        allowed_next = ALLOWED_TRANSITIONS.get(candidate.stage, [])
        if next_stage in allowed_next:
            candidate.stage = next_stage
            session.add(candidate)
            session.commit()
    return RedirectResponse(f"/hiring/{candidate_id}", status_code=303)