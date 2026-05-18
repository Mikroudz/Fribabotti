import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/tracks')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/tracks"!</div>
}
