describe('Speech to Note app', () => {
  it('renders the app header', () => {
    cy.visit('/')
    cy.contains('h1', 'Speech to Note')
  })
})