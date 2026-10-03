# Architecture and Flow Documentation

## 1. حدود التوثيق

هذا المستند يصف المسار المرجعي في `latest/`. المجلدان `org/` و`cv/` وملفات HTML/Arduino الجذرية تمثل تجارب أو نسخاً سابقة، وقد تختلف في البروتوكول.

## 2. مراحل الرؤية

```mermaid
flowchart TD
    S[HTTP frame] --> V{Frame valid?}
    V -->|No| E1[Report capture failure]
    V -->|Yes| C{Corners available?}
    C -->|JSON| P[Use calibrated points]
    C -->|Model| M[Infer corner boxes]
    M --> O[Order four points]
    P --> W[Perspective transform]
    O --> W
    W --> G[800x800 board]
    G --> Y[Gray + blur]
    Y --> T[8x8 center crops]
    T --> R[Resize to 90x90]
    R --> Q[SSIM per square]
    Q --> D[Changed-square candidates]
```

المعادلة المفاهيمية لكل مربع:

```text
changed(square) = SSIM(reference_square, current_square) < threshold
```

في النسخة الحالية العتبة الموثقة في الكود هي `0.99`. هذه ليست قيمة عامة صالحة لكل كاميرا أو إضاءة، بل parameter تجريبي يحتاج معايرة.

## 3. تفسير النقلة

```mermaid
flowchart LR
    A[Changed squares] --> B[Special castling patterns]
    A --> C[Candidate source/target pair]
    B --> D[Observed set]
    C --> D
    D --> E[Enumerate legal moves]
    E --> F[Expected visual diff per move]
    F --> G[Symmetric difference]
    G --> H{Best result}
    H -->|Exact unique| I[Accept]
    H -->|Several exact| J[Ambiguous]
    H -->|Near match| K[Relaxed candidate]
    H -->|No match| L[Illegal/reject]
```

الفكرة المهمة هنا أن الرؤية لا تغيّر اللوحة مباشرة. يتم أولاً توليد النقلات القانونية من `python-chess`، ثم مقارنة أثر كل نقلة بالمربعات المرصودة.

## 4. تنفيذ حركة الروبوت

```mermaid
sequenceDiagram
    participant GC as GameController
    participant E as Engine
    participant R as RobotMoveExecutor
    participant A as ArduinoArm
    participant M as Microcontroller
    participant V as Vision

    GC->>E: request_move(board)
    E-->>GC: expected_move
    GC->>R: execute(expected_move)
    R->>A: move to REF / source / target
    A->>M: six angles over Serial
    M-->>A: BUTTON_PRESSED
    A-->>R: move complete
    GC->>V: capture verification frame
    V-->>GC: changed squares
    GC->>GC: compare observed move with expected move
```

## 5. السلامة الحالية

- الحركة التدريجية للمحركات تقلل القفزات المفاجئة لكنها لا تغني عن limit switches أو مراقبة تيار.
- زر التأكيد يمنع الانتقال إلى الدورة التالية قبل إشارة المستخدم/الروبوت.
- لا توجد في النسخة الحالية آلية شاملة لإيقاف آمن أو rollback عند فشل خطوة وسطية؛ يجب اعتبار ذلك خطراً معروفاً.
- لا ينبغي تشغيل الذراع قرب اليد أو الوجه أو الأشياء القابلة للكسر.

## 6. عقود البيانات

### `board_corners.json`

```json
{
  "points": [
    [x_top_left, y_top_left],
    [x_top_right, y_top_right],
    [x_bottom_right, y_bottom_right],
    [x_bottom_left, y_bottom_left]
  ]
}
```

### `robot_arm_poses.json`

تحتوي كل وضعية على زوايا المفاصل الخمسة التي يكمّلها adapter بزاوية القبضة. المفاتيح المتوقعة هي مربعات الشطرنج مع `REF` و`THROW`. يجب اعتماد الملف الفعلي في `latest` كمصدر الحقيقة وعدم خلطه مع ملف `chess-robot-positions.json` ذي البنية القديمة.

