import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/tracks/$trackId')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/tracks/$trackId"!</div>
}
