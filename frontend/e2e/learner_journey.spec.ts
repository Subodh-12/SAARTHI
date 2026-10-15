import { test, expect } from "@playwright/test";

test.describe("SAARTHI — End-to-End Learner Journey (Mobile PWA)", () => {
  test("complete learner journey: onboarding, lesson, doubt, progress, dev diagnostics", async ({
    page,
  }) => {
    // 1. Initial startup — onboarding screen
    await page.goto("/");
    await expect(page).toHaveTitle(/ସାରଥି/);

    // If onboarding is shown, fill in profile name and submit
    const createBtn = page.getByRole("button", { name: "ସୃଷ୍ଟି କରନ୍ତୁ" });
    if (await createBtn.isVisible({ timeout: 4000 })) {
      const nameInput = page.getByRole("textbox").first();
      await nameInput.fill("ସୁବୋଧ");
      await createBtn.click();
    }

    // 2. Home screen verification
    const homeTab = page.locator("button:has-text('ମୁଖ୍ୟ')");
    await expect(homeTab).toBeVisible({ timeout: 8000 });

    // Header displays app title
    const headerTitle = page.locator("header");
    await expect(headerTitle).toContainText("SAARTHI");

    // 3. Navigation to Lesson screen
    const lessonTab = page.locator("button:has-text('ପାଠ')");
    await lessonTab.click();
    await expect(page.locator(".card").first()).toBeVisible({ timeout: 8000 });

    // 4. Doubt screen — asking a question
    const doubtTab = page.locator("button:has-text('ପ୍ରଶ୍ନ')");
    await doubtTab.click();
    const doubtInput = page.locator("textarea, input[type='text']").first();
    await expect(doubtInput).toBeVisible({ timeout: 6000 });

    await doubtInput.fill("ପଦାର୍ଥ କଣ?");
    const askBtn = page.locator("button:has-text('ପଚାରନ୍ତୁ')").first();
    await askBtn.click();

    // Expect an answer bubble or response card
    await expect(page.locator(".card").first()).toBeVisible({ timeout: 10000 });

    // 5. Progress screen — concept map
    const progressTab = page.locator("button:has-text('ପ୍ରଗତି')");
    await progressTab.click();
    await expect(page.locator("text=ଧାରଣା ମାନଚିତ୍ର")).toBeVisible({ timeout: 8000 });
    // Mastery bands legend is visible
    await expect(page.locator("text=ଶିଖିଲା")).toBeVisible();

    // 6. Developer panel — diagnostics & traces
    const devTab = page.locator("button:has-text('ଡାକ')");
    await devTab.click();
    await expect(page.locator("button:has-text('Sync & Outbox')")).toBeVisible({ timeout: 6000 });

    // Switch to Pack & Storage tab in Developer panel
    const packStorageDevBtn = page.locator("button:has-text('Pack & Storage')");
    await packStorageDevBtn.click();
    await expect(page.locator("text=Device Storage Budget")).toBeVisible();
  });
});
