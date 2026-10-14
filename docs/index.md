---
layout: page
title: Home
permalink: /
---

<div class="hero-card">
  <h1>Home Model Workshop</h1>
  <p><strong>A Blender add-on for guided room layout and editable house-model blockouts.</strong></p>
  <p>
    Home Model Workshop helps you start from a room program and a visual placement guide, arrange the rooms yourself, validate the layout, and build floors and walls from the room footprints. It is designed as a blockout and layout tool, not an automatic architectural designer.
  </p>
  <blockquote>
    <p><strong>Beta note:</strong> Home Model Workshop 0.1.0 was built and smoke-tested in Blender 5.2.2. Generated models are editable blockouts and should be reviewed in Blender before further use. Blender 4.2.0 is the declared minimum version in the extension manifest, but compatibility with Blender 4.2 has not been independently verified.</p>
  </blockquote>
</div>

<div class="feature-grid">

  <div class="card">
    <h3>Start here</h3>
    <ul>
      <li><a href="{{ '/getting-started/' | relative_url }}">Getting Started</a></li>
      <li><a href="{{ '/user-guide/' | relative_url }}">User Guide</a></li>
      <li><a href="{{ '/developer-guide/' | relative_url }}">Developer Guide</a></li>
    </ul>
  </div>

  <div class="card">
    <h3>What it does</h3>
    <ul>
      <li>Creates editable room footprints from starter plans or imported meshes</li>
      <li>Uses Box, L, H, and U visual placement guides</li>
      <li>Lets you arrange rooms manually before building the model</li>
      <li>Validates overlaps and opening-guide issues before rebuilds</li>
      <li>Builds floors, walls, and optional room labels from the room footprints</li>
    </ul>
  </div>

  <div class="card">
    <h3>Quick workflow</h3>
    <ol>
      <li>Install and enable the add-on.</li>
      <li>Choose a starter guide shape and room set.</li>
      <li>Create the starter plan.</li>
      <li>Move and resize the room footprints into the layout you want.</li>
      <li>Validate the layout.</li>
      <li>Build or rebuild the house model.</li>
    </ol>
  </div>

  <div class="card">
    <h3>Notes</h3>
    <ul>
      <li>The guide is visual only; the room footprints define the final layout.</li>
      <li>Rooms do not need to fill the guide.</li>
      <li>Hallways and circulation areas are placed manually.</li>
      <li>Open gaps stay open and shared room edges create one wall.</li>
    </ul>
  </div>

</div>

<div class="section-note">
  For a full step-by-step walkthrough, open the <a href="{{ '/getting-started/' | relative_url }}">Getting Started guide</a>.
</div>

## Project status

Home Model Workshop is currently in beta. The focus is on editable blockout workflows, clear validation, and practical manual control over the final layout.
