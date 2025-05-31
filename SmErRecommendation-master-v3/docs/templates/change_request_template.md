
# Change Request (CR)  

## CR Information  
- **CR ID**: CR-2025-001  
- **Date**: 2025-04-18  
- **Requested By**: Xu Yixin (Product Owner)  
- **Priority**: High  
- **Status**: Approved (Updated after FTR approval on 2025-04-20)  


## Change Description  
### Purpose  
Add a **recommendation module** for escape rooms and a **comment interaction module** to the appointment management system, enhancing user personalization and feedback collection.  

### Scope  
- **Affected Systems**: Frontend (React), Backend (Django), Database (MySQL), User Authentication Module.  
- **Target Components**: Recommendation algorithm, user comment database schema, frontend display components.  

### Current State  
- The system lacks personalized escape room recommendations, relying on basic search filters.  
- No user comment or rating functionality exists, limiting user engagement and data-driven improvements.  

### Proposed Changes  
1. Develop a hybrid recommendation algorithm (content-based filtering + collaborative filtering) using the `Surprise` library, incorporating user booking history and escape room tags.  
2. Implement a `Review` model in Django to store user comments, ratings, and sentiment analysis results (via TextBlob).  
3. Build frontend components for recommendation lists (with tag-based filtering) and comment submission/display (including sentiment tags like "Positive" or "Neutral").  


## Impact Analysis  
### Affected Components  
- **Backend**:  
  - Components: Recommendation engine, comment API endpoints, database ORM.  
  - Files: `scripts/models.py`, `scripts/views.py`, `scripts/urls.py`, `recommendation/algo.py`.  
- **Frontend**:  
  - Components: Recommendation list view, comment submission form, sentiment display.  
  - Files: `src/components/RecommendationList.jsx`, `src/components/CommentSection.jsx`.  
- **Database**: New table `reviews`; modified `scripts` table to add `tags` field for content-based filtering.  

### Dependencies  
- **Prerequisites**: Install `Surprise`, `TextBlob`, and `Django-filter` packages.  
- **Dependent Tasks**: T3 (System Design for Recommendation Logic), T5 (UI/UX Design for Comment Interface).  

### Risks  
| **Potential Risks**                | **Mitigation Strategies**                                  |  
|------------------------------------|----------------------------------------------------------|  
| Algorithm performance degradation  | Conduct load testing with JMeter; optimize database indexing for `script_id` and `user_id`. |  
| Cold-start user recommendation failure | Add a fallback mechanism using popular escape room tags (e.g., "Horror", "Mystery") for users with no booking history. |  


## Implementation Plan  
### Steps  
1. **Backend Development (2025-04-20–2025-05-05)**  
   - Qiao Xi: Define `Review` model and API endpoints (`/api/reviews/` for comments, `/api/recommendations/` for escape room suggestions).  
   - Tao Yanerge: Develop recommendation algorithm in `recommendation/algo.py`, integrating user history and escape room tags; implement cold-start fallback logic.  

2. **Frontend Development (2025-05-06–2025-05-15)**  
   - Tao Yanerge: Build a dynamic recommendation list component with tag-based filtering (e.g., "Difficulty: Hard").  
   - Xu Yixin: Design a comment submission form with star ratings and real-time sentiment feedback display.  

3. **Testing & Deployment (2025-05-16–2025-05-20)**  
   - Cai Xinyi: Conduct unit tests for API endpoints; perform security scans for comment input validation.  
   - Team: Deploy to a staging environment for user acceptance testing (UAT) with 20 beta users, verifying recommendation accuracy and comment functionality.  

### Testing Requirements  
- **Test Cases**:  
  1. Validate that recommendations update when a user submits a new rating.  
  2. Ensure comment submission triggers sentiment analysis and updates the `reviews` table.  
- **Test Scenarios**:  
  - Edge Case: User with no booking history receives recommendations based on popular tags.  
  - High Concurrency: 500+ users submit comments simultaneously to test database performance.  
- **Acceptance Criteria**:  
  - Recommendations match user preferences with ≥85% accuracy in UAT.  
  - Comment loading time ≤2 seconds for 100+ comments.  

### Rollback Plan  
- If deployment fails, revert to the last stable commit using `git checkout a1b2c3d` (pre-change commit).  
- Restore the database from a backup taken before creating the `reviews` table via `mysql -u root -p < backup_20250417.sql`.  


## Review and Approval  
### Technical Review  
- **Reviewer 1: Sun Anchen (External Reviewer, Algorithm Expert)**  
  - Date: 2025-04-20  
  - Comments:  
    "Recommendation algorithm design is well-structured and aligns with industry best practices. Suggest adding a cold-start fallback using popular escape room tags to improve user experience for new users."  
- **Reviewer 2: Tao Yanerge (Software Engineer, Internal)**  
  - Date: 2025-04-19  
  - Comments:  
    "Database schema for `reviews` is efficient. Indexing `script_id` and `user_id` will optimize query performance for recommendations."  
- **Reviewer 3: Qiao Xi (Software Engineer, Internal)**  
  - Date: 2025-04-19  
  - Comments:  
    "API endpoints are RESTful and well-documented. Error handling for edge cases (e.g., empty user history) is appropriately implemented."  

### Final Approval  
- **Approver: Cai Xinyi (Scrum Master)**  
  - Date: 2025-04-20  
  - Comments:  
    "FTR successfully passed with expert input from Sun Anchen. Cold-start fallback logic is added as a follow-up task (TASK-123). Proceed with implementation."  


## Implementation Status  
- [x] Code changes completed (Qiao Xi, 2025-05-05)  
- [x] Unit tests written and passed (Cai Xinyi, 2025-05-06)  
- [ ] Integration tests completed (Scheduled: 2025-05-17)  
- [x] Documentation updated (Xu Yixin, 2025-05-07, including FTR review notes)  
- [x] Code review completed (Tao Yanerge, 2025-05-08, aligned with FTR feedback)  
- [x] Final approval received (Cai Xinyi, 2025-05-08)  


## Notes  
- **FTR Key Outcome**: External reviewer Sun Anchen’s feedback improved cold-start handling, ensuring new users receive relevant recommendations without booking history.  
- **Action Item**: Cold-start fallback logic (using popular escape room tags) was implemented in `recommendation/algo.py` (commit: a1b2c3d, Qiao Xi, 2025-05-03).  
- **Collaboration Note**: Coordinate with the design team to ensure the comment module’s UI/UX matches the system’s visual consistency.
