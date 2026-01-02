# TDD Guidelines for Meeting Facilitator AI

## 🎯 Test-Driven Development Strategy

### Overview
Detta dokument beskriver TDD-approach för Meeting Facilitator AI-projektet. Vi följer **Red-Green-Refactor** cykeln för att bygga in kvalitet från start.

### Test Pyramid
```
    🔬 E2E Tests (5%)
       ↑
   🧪 Integration Tests (15%)  
       ↑
  ✅ Unit Tests (80%)
```

## 📋 Test Categories

### 1. Unit Tests (80%)
- **Backend**: Services, models, utilities
- **Frontend**: Hooks, utilities, components
- **Coverage**: >90% för critical paths

### 2. Integration Tests (15%)
- **API endpoints**: Full request/response cycles
- **Database**: Model interactions
- **WebSocket**: Connection handling

### 3. E2E Tests (5%)
- **Full meeting flow**: Create → Record → Analyze → Protocol
- **Critical user journeys**

## 🔄 TDD Workflow

### Red Phase
1. **Skriv ett failing test**
   - Beskriv exakt vad du vill implementera
   - Testet ska misslyckas med tydligt felmeddelande
   
### Green Phase  
2. **Gör testet pass**
   - Minimal implementation för att få testet att grönas
   - Inga extra features, bara det nödvändigaste
   
### Refactor Phase
3. **Förbättra koden**
   - Clean code, DRY, SOLID principles
   - Behåll alla tests gröna

## 📝 Test Naming Conventions

### Backend (pytest)
```python
class TestServiceName:
    def test_method_scenario_expected_result(self):
        """Test description in Swedish."""
        pass
    
    def test_invalid_input_raises_error(self):
        """Test error handling."""
        pass
```

### Frontend (vitest)
```typescript
describe('ComponentName', () => {
  it('should behave correctly when scenario', () => {
    // Test implementation
  })
  
  it('should handle error case', () => {
    // Error handling test
  })
})
```

## 🛠️ Test Structure

### Backend Test Structure
```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_api/               # API endpoint tests
│   ├── test_meetings.py
│   ├── test_audio.py
│   └── test_protocols.py
├── test_services/          # Business logic tests
│   ├── test_idoarrt_service.py
│   ├── test_claude_service.py
│   └── test_transcription_service.py
├── test_models/            # Database model tests
└── test_integration/       # Integration tests
    └── test_meeting_flow.py
```

### Frontend Test Structure
```
frontend/src/
├── test/
│   └── setup.ts           # Global test setup
├── hooks/
│   └── *.test.ts          # Hook tests
├── components/
│   └── *.test.tsx         # Component tests
├── services/
│   └── *.test.ts          # Service tests
└── utils/
    └── *.test.ts          # Utility tests
```

## 🎯 Test Coverage Goals

### Critical Components (>95%)
- IDOARRT parsing & validation
- Audio recording & upload
- Claude API integration
- Meeting state management

### Important Components (>80%)
- WebSocket connections
- Protocol generation
- UI components

### Support Components (>60%)
- Utilities
- Error handling
- Logging

## 📊 Quality Gates

### Pre-commit Checks
```bash
# Backend
ruff check .              # Linting
mypy app/                 # Type checking  
pytest --cov=app         # Test coverage

# Frontend
npm run lint              # ESLint
npm run typecheck         # TypeScript
npm run test:coverage     # Test coverage
```

### CI/CD Pipeline
- **All tests must pass**
- **Coverage targets met**
- **Security scans clear**
- **No new vulnerabilities**

## 🧪 Test Data Management

### Fixtures
- **Deterministic data**: Use predefined test data
- **Isolation**: Each test independent
- **Cleanup**: Automatic teardown

### Mocking Strategy
- **External APIs**: Always mock (Claude, transcription)
- **Browser APIs**: Mock MediaRecorder, WebSocket
- **Database**: Use in-memory SQLite

## 📋 Test Examples

### Backend Service Test
```python
def test_parse_valid_idoarrt_success(self, sample_idoarrt_markdown):
    """Test parsing valid IDOARRT markdown."""
    # When
    result = self.service.parse_idoarrt(sample_idoarrt_markdown)
    
    # Then
    assert result["intent"] == "Testa mötesfacilitering"
    assert len(result["desired_outcomes"]) == 2
```

### Frontend Hook Test
```typescript
it('should start recording when start button is clicked', async () => {
  const user = userEvent.setup()
  render(<TestComponent onChunkReady={mockChunkReady} />)
  
  await user.click(screen.getByText('Start'))
  
  expect(screen.getByTestId('is-recording')).toHaveTextContent('true')
})
```

### Integration Test
```python
def test_full_meeting_lifecycle(self, integration_client):
    """Test complete meeting from creation to protocol."""
    # Create meeting
    # Start meeting  
    # Upload audio
    # Generate protocol
    # Verify all steps
```

## 🚀 Best Practices

### DO ✅
- **Write tests first** (TDD)
- **Test one thing per test**
- **Use descriptive test names**
- **Mock external dependencies**
- **Keep tests fast and isolated**
- **Test edge cases and errors**
- **Maintain high coverage**

### DON'T ❌
- **Don't test implementation details**
- **Don't skip tests for "simple" code**
- **Don't use shared state between tests**
- **Don't ignore flaky tests**
- **Don't mock everything indiscriminately**

## 🔧 Running Tests

### Backend
```bash
cd backend
pytest                           # All tests
pytest tests/test_services/       # Service tests only
pytest --cov=app                 # With coverage
pytest -v                        # Verbose output
```

### Frontend
```bash
cd frontend
npm test                         # All tests
npm run test:ui                  # Interactive UI
npm run test:coverage            # With coverage
```

### Integration
```bash
cd backend
pytest tests/test_integration/   # Full flow tests
```

## 📈 Metrics & Monitoring

### Coverage Reports
- **Backend**: `coverage/` directory
- **Frontend**: `coverage/` directory  
- **CI**: Codecov integration

### Quality Metrics
- **Test count**: Track growth
- **Coverage percentage**: Maintain >80%
- **Test duration**: Keep fast
- **Flaky test rate**: Zero tolerance

## 🎯 Next Steps

1. **Implement missing test coverage**
2. **Add performance tests**  
3. **Set up monitoring dashboards**
4. **Create test data generators**
5. **Automate regression testing**

---

**Remember**: "If it's not tested, it's broken." - TDD Mantra
