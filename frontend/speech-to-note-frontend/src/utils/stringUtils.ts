export const isContentEmpty = (content: string): boolean => {
  if (!content) return true
  // Remove HTML tags and check if there's any meaningful text
  const textOnly = content.replace(/<[^>]*>/g, '').trim()
  return textOnly.length === 0
}
